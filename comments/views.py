from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render
import json
import pytz
import re
import requests
import timeago
from dynamic_db_router import in_database
from datetime import datetime, timedelta
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from django.db.models import Q
from django.http import Http404, HttpResponsePermanentRedirect
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.http import HttpResponse

# Call myroot properties
from myroot.views.vcommon import (dict_alert_msg, math_divide,
                                  convertToLocalDateTime, get_is_super_user,
                                  is_email_valid)

# Call bp properties
from bp.models import (Business, BusinessTag, BusinessComment,
                       BusinessReview, BusinessInquiry,
                       BusinessNotifications, BusinessNotificationsRead)

from bp.common import (get_bl_by_user_id_dashboard, get_bp_tags, get_bp_logo,
                       get_bl_by_id_dashboard, get_related_bp, get_bp_reviews,
                       load_bp_reviews, sum_bp_reviews_rate, get_bp_comments,
                       load_bp_comments, get_bl_by_id, get_bp_inquiries,
                       bp_tagged_bl_list, get_bp_inquires,
                       get_bp_reviews_list, get_bp_inquiries_list,
                       get_bp_comments_list, get_comment_data, get_inquiry_data,
                       get_review_data, get_business_tags,
                       get_created_by_from_inquiry_id, get_created_by_from_review_id,
                       get_created_by_from_comment_id)

from bp.forms import (BusinessForm, BPCommentForm, BPReviewForm, BPInquiryForm)

from bp.tasks import (bp_comment_send_mail, bp_review_send_mail,
                      bp_inquiry_send_mail, mark_all_read_notifications_bp)

# Call medialab properties
from medialab.models import (MediaLab, MediaLabUsedFiles)

# Call easy_thumbnails properties
from easy_thumbnails.files import get_thumbnailer


@login_required
def mybusinesslistings_view(request):
    """Renders the my business listings page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        # Set session for the main left side bar active menu
        request.session['active_sidebar_menu'] = "mybusinesslistings"

        # Get latest 50 business listings
        bl_data = get_bl_by_user_id_dashboard(current_user.id, 50, is_super_user)

        return render(request, 'bp/index.html',
                      {
                          'title': 'Business Listings',
                          'meta_desc': 'Manage your business listings',
                          'bl_data': bl_data,
                          'is_super_user': is_super_user
                       })


@login_required
def search_bp_text_view(request):
    """Renders the business listing search text."""
    if request.method == "POST":
        fsearch = request.POST.get('fsearch')

        # Get user info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        if is_super_user:
            # Display images list, icontains=is not case sensitive
            data_lists = Business.objects.using(
                    settings.APP_LABEL_BP).filter(
                            Q(is_deleted=False) &
                            (Q(company_name__icontains=fsearch) |
                            Q(address__icontains=fsearch) |
                            Q(short_desc__icontains=fsearch) |
                            Q(about__icontains=fsearch))).order_by('company_name')[:50]
        else:
            # Display images list, icontains=is not case sensitive
            data_lists = Business.objects.using(
                    settings.APP_LABEL_BP).filter(
                            Q(created_by=current_user.id) &
                            Q(is_deleted=False) &
                            (Q(company_name__icontains=fsearch) |
                            Q(address__icontains=fsearch) |
                            Q(short_desc__icontains=fsearch) |
                            Q(about__icontains=fsearch))).order_by('company_name')[:50]

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            url = settings.BASE_URL + slugify(fh.company_name) + "-" + str(fh.id) + '-bp'
            trun_address = fh.address[:100] + '...'

            # Convert UTC datetime from db to user's local datetime.
            created_date = convertToLocalDateTime(fh.created_date)

            edit_url = settings.BASE_URL + "bp/" + str(fh.id) + "/change/"

            fh_list.append(
                    {'company_name': (fh.company_name),
                     'address': trun_address,
                     'created_date': created_date,
                     'is_active': fh.is_active,
                     'id': fh.id,
                     'url': url,
                     'edit_url': edit_url,
                     'is_super_user': is_super_user
                     })

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


@login_required
def search_bp_dr_view(request):
    """Renders the business listing search records by created_date."""
    if request.method == "POST":

        # Get date range values from user input
        mStartDate = request.POST.get('mStartDate')
        mEndDate = request.POST.get('mEndDate')

        # Format date
        date_format = '%Y-%m-%d'

        unaware_start_date = datetime.strptime(mStartDate, date_format)
        aware_start_date = pytz.utc.localize(unaware_start_date)

        unaware_end_date = datetime.strptime(mEndDate, date_format
                                             ) + timedelta(days=1)
        aware_end_date = pytz.utc.localize(unaware_end_date)

        # Get user info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        if is_super_user:
            # Display data, icontains=is not case sensitive
            data_lists = Business.objects.using(
                    settings.APP_LABEL_BP).filter(
                                is_deleted=False,
                                created_date__range=(aware_start_date,
                                                     aware_end_date)
                                ).order_by('company_name')[:50]
        else:
            # Display data, icontains=is not case sensitive
            data_lists = Business.objects.using(
                    settings.APP_LABEL_BP).filter(
                                created_by=current_user.id,
                                is_deleted=False,
                                created_date__range=(aware_start_date,
                                                     aware_end_date)
                                ).order_by('company_name')[:50]

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            url = settings.BASE_URL + slugify(fh.company_name) + "-" + str(fh.id) + '-bp'
            trun_address = fh.address[:100] + '...'

            # Convert UTC datetime from db to user's local datetime.
            created_date = convertToLocalDateTime(fh.created_date)

            edit_url = settings.BASE_URL + "bp/" + str(fh.id) + "/change/"

            fh_list.append(
                    {'company_name': (fh.company_name),
                     'address': trun_address,
                     'created_date': created_date,
                     'is_active': fh.is_active,
                     'id': fh.id,
                     'url': url,
                     'edit_url': edit_url,
                     'is_super_user': is_super_user
                     })

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


@login_required
def del_row_bp_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        # Current user logged in info
        current_user = request.user

        # Just update 'is_deleted=False' status of the row only
        Business.objects.using(settings.APP_LABEL_BP).filter(
                id=row_id).update(is_deleted=True,
                                  deleted_by=current_user.id,
                                  deleted_date=timezone.now())

        # Return some json response back to user
        msg = """Your deletion was successful, thank you!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        return JsonResponse(data)


@login_required
def add_bp_view(request):
    """Renders the add new business listing page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user
        formAddBP = BusinessForm()

        return render(request, 'bp/add_bp.html',
                      {
                          'title': 'Add Business Listing',
                          'meta_desc': 'Add new business listing',
                          'formAddBP': formAddBP
                       })

    data = dict()
    if request.method == "POST":
        # Access myroot database
        with in_database(settings.APP_LABEL_BP, write=True):

            form = BusinessForm(request.POST)
            selected_tags = request.POST.get('selected_tags')
            saveType = request.POST.get('saveType')
            about = request.POST.get('about')

            # Current user logged in info
            current_user = request.user

            if form.is_valid():

                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GRECAP_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post(settings.GRECAP_VERIFY_URL, data=data)
                result = r.json()
                ''' End reCAPTCHA validation '''

                if result['success']:

                    # Save new data
                    new_bp = form.save(commit=False)
                    new_bp.created_by = current_user.id
                    new_bp.modified_by = current_user.id
                    new_bp.modified_date = timezone.now()

                    # Check saveType if it's 'Publish' or 'Draft'
                    if saveType == "Draft":
                        new_bp.is_active = False
                    else:
                        new_bp.is_active = True

                    # Insert all <a href> tag with rel="nofollow" tag
                    r_nofollow = re.compile('<a (?![^>]*nofollow)')
                    s_nofollow = '<a rel="nofollow" '
                    about_cleaned = r_nofollow.sub(s_nofollow, about)

                    new_bp.about = about_cleaned
                    new_bp.save()  # Finally save the form data
                    new_bp.pk  # Get latest primary key

                    # Split all commas ',' for all the tags submitted
                    tags = selected_tags.split(",")
                    for t in tags:
                        tag = t.strip()

                        if tag:
                            # Insert new business tags to the BusinessTag master table
                            BusinessTag.objects.create(business_id=new_bp.pk,
                                                       tag_name=tag.lower(),
                                                       tag_name_slug=slugify(tag),
                                                       is_active=True,
                                                       created_by=current_user.id)

                    # Return some json response back to user
                    msg = """ Your business listing was successfully saved, thank you! """
                    data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                else:

                    # Return some json response back to user
                    msg = """Invalid reCAPTCHA, please try again."""
                    data = dict_alert_msg('False', 'Oops, Error', msg, 'error')
            else:

                # Extract form.errors
                msg = None
                msg = [(k, v[0]) for k, v in form.errors.items()]
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            return JsonResponse(data)


@login_required
def get_all_user_business_tags_json_view(request):
    """Fetch all business tags previously used by the user."""
    if request.method == "POST":

        # Get user info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        if is_super_user:
            # For admin, it's too many
            data_lists = BusinessTag.objects.using(settings.APP_LABEL_BP).filter(
                    is_active=True, is_deleted=False, business_id=0)
        else:
            data_lists = BusinessTag.objects.using(settings.APP_LABEL_BP).filter(
                    created_by=current_user.id, is_active=True, is_deleted=False)

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            fh_list.append(
                    {'tag_name': fh.tag_name})

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


@login_required
def change_bp_view(request, id):
    """Renders the change business listing page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        # Check if valid access rights
        if is_super_user:
            bp_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                    id=id, is_deleted=False)
        else:
            bp_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                    id=id, created_by=current_user.id, is_deleted=False)

        if bp_data:
            # Edit form data
            edit_data = Business.objects.using(settings.APP_LABEL_BP).get(
                    id=id, is_deleted=False)

            formAddBP = BusinessForm(instance=edit_data)

            # Get link data common fields
            company_name_slug = ""

            for b in bp_data:
                company_name_slug = slugify(b.company_name)

            # Get tags
            tag_list = get_bp_tags(id)

            # Display images list
            img_lists = MediaLab.objects.filter(
                uploaded_by=current_user.id).order_by('-uploaded_date')[:16]

            # Get company logo
            featured_image, is_featured_image_found, image_id = get_bp_logo(id, current_user.id, is_super_user)

            return render(request, 'bp/change_bp.html',
                          {
                              'title': 'Change Business Listing',
                              'meta_desc': 'Manage to update your business listing',
                              'business_id': id,
                              'company_name_slug': company_name_slug,
                              'formAddBP': formAddBP,
                              'tag_list': tag_list,
                              'img_lists': img_lists,
                              'featured_image': featured_image,
                              'is_featured_image_found': is_featured_image_found,
                              'image_id': image_id
                           })
        else:
            raise Http404()

    data = dict()
    if request.method == "POST":
        # Access myroot database
        with in_database(settings.APP_LABEL_BP, write=True):

            form_edit = BusinessForm(request.POST)
            selected_tags = request.POST.get('selected_tags')
            saveType = request.POST.get('saveType')
            business_id = request.POST.get('business_id')
            about = request.POST.get('about')

            # Prepare the url to redirect from old to new
            url = slugify(request.POST.get('company_name'))

            # Current user logged in info
            current_user = request.user

            if form_edit.is_valid():

                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GRECAP_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post(settings.GRECAP_VERIFY_URL, data=data)
                result = r.json()
                ''' End reCAPTCHA validation '''

                if result['success']:
                    # Update data
                    if Business.objects.filter(id=business_id, is_deleted=False).exists():

                        # Get the form edit instance
                        update_data = Business.objects.get(id=business_id,
                                                           is_deleted=False)
                        form_edit = BusinessForm(request.POST, instance=update_data)

                        # Update data
                        new_bp = form_edit.save(commit=False)
                        new_bp.modified_by = current_user.id
                        new_bp.modified_date = timezone.now()

                        # Check saveType if it's 'Publish' or 'Draft'
                        if saveType == "Draft":
                            new_bp.is_active = False
                        else:
                            new_bp.is_active = True

                        # Insert all <a href> tag with rel="nofollow" tag
                        r_nofollow = re.compile('<a (?![^>]*nofollow)')
                        s_nofollow = '<a rel="nofollow" '
                        about_cleaned = r_nofollow.sub(s_nofollow, about)

                        new_bp.about = about_cleaned
                        new_bp.save()  # Finally save the form data

                        # Check if business_id existed & must marked as in-active & is_deleted=True
                        BusinessTag.objects.filter(business_id=business_id).update(is_active=False, is_deleted=True)

                        # Split all commas ',' for all the tags submitted
                        tags = selected_tags.split(",")
                        for t in tags:
                            tag = t.strip()

                            if tag:
                                # Insert new tags to the Tag master table
                                BusinessTag.objects.create(business_id=business_id,
                                                           tag_name=tag.lower(),
                                                           tag_name_slug=slugify(tag),
                                                           is_active=True,
                                                           created_by=current_user.id)

                        # Return some json response back to user
                        msg = """ Your business listing was successfully modified, thank you! """
                        data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                    else:
                        # Return some json response back to user
                        msg = """ The data has no longer existed, the update has been aborted! """
                        data = dict_alert_msg('True', 'Update Failed!', msg, 'error')
                else:

                    # Return some json response back to user
                    msg = """Invalid reCAPTCHA, please try again."""
                    data = dict_alert_msg('False', 'Oops, Error', msg, 'error')
            else:

                # Extract form.errors
                msg = None
                msg = [(k, v[0]) for k, v in form_edit.errors.items()]
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            return JsonResponse(data)


@login_required
def change_company_logo_view(request):
    """Change company logo."""
    data = dict()
    if request.method == 'POST':
        fid = request.POST.get('fid')
        fname = request.POST.get('fname')
        ref_id = request.POST.get('ref_id')

        # Get currently login user
        current_user = request.user

        # Check if 'ref_id' exist from the source table
        if Business.objects.using(settings.APP_LABEL_BP).filter(id=ref_id).exists():
            if MediaLab.objects.filter(id=fid).exists():
                # Check if used file exist
                if MediaLabUsedFiles.objects.filter(
                        used_by_user_id=current_user.id,
                        ref_id=ref_id,
                        src_type=settings.REF_USED_BP).exists():

                    # Update existing company logo
                    MediaLabUsedFiles.objects.filter(
                            used_by_user_id=current_user.id,
                            src_type=settings.REF_USED_BP,
                            ref_id=ref_id).update(src_id=fid,
                                                  used_date=timezone.now())
                else:
                    # Insert for the first time the company logo
                    MediaLabUsedFiles.objects.create(
                            src_id=fid, src_type=settings.REF_USED_BP,
                            ref_id=ref_id,
                            used_by_user_id=current_user.id)

                # easy_thumbnails create crop in python
                options = {'size': (150, 100), 'autocrop': True, 'crop': 'smart', 'upscale': True}
                thumb_url = get_thumbnailer(fname).get_thumbnail(options).url

                # Return some json response back to user
                msg = """ Your new company logo was successfully changed, thank you! """
                data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                data["is_changed"] = True
                data["thumb_url"] = thumb_url
                data["fid"] = fid

            else:

                # Return some json response back to user
                msg = """ Oops!, something went wrong, changing new company logo failed! """
                data = dict_alert_msg('True', 'Company Logo Not Changed!', msg, 'error')

                data["is_changed"] = False
        else:

            # Return some json response back to user
            msg = """ Oops!, reference1 id can't be found! """
            data = dict_alert_msg('True', 'Invalid Reference ID!', msg, 'error')

            data["is_changed"] = False

        return JsonResponse(data)


def bp_view(request, slug, id):
    """Renders the business profile page."""
    if request.method == 'GET':

        # Current user logged in info
        current_user = request.user

        # Get match link data by id
        bl_data = get_bl_by_id_dashboard(id)

        if bl_data.count():

            company_name = ''
            address = ''
            office_hours = ''
            short_desc = ''
            tel_no = ''
            fax_no = ''
            website = ''
            about = ''
            meta_title = ''
            meta_desc = ''
            is_active = ''
            created_by = ''
            created_date = ''
            modified_date = ''

            for bp in bl_data:
                company_name = bp.company_name
                address = bp.address
                tel_no = bp.tel_no
                fax_no = bp.fax_no
                website = bp.website
                about = bp.about
                office_hours = bp.office_hours
                short_desc = bp.short_desc
                is_active = bp.is_active
                created_by = bp.created_by
                created_date = bp.created_date
                modified_date = bp.modified_date

            # Get Meta Title, priority short_desc if enough length
            if len(short_desc.strip()) > 80:
                meta_desc = """{s1} | {s2}, {s3}""".format(
                        s1=settings.APP_SHORTNAME,
                        s2=str(id),
                        s3=short_desc)
            else:
                # Just put company address, tel no, fax no
                meta_desc = """{s1}, Tel Nos: {s2}, Fax Nos: {s3}, {s4} - {s5} |
                {s6}""".format(s1=address, s2=tel_no, s3=fax_no, s4=about,
                               s5=settings.APP_SHORTNAME, s6=str(id))

            # Get Page Title
            meta_title = company_name[:40] + ' | ' + str(id)

            # Get first tag name
            ft = BusinessTag.objects.using(settings.APP_LABEL_BP).filter(
                    business_id=id, is_active=True, is_deleted=False
                    ).order_by('id')[:1]

            first_tag_id = 0
            first_tag_name = ""
            first_tag_slug = ""

            for f in ft:
                first_tag_id = f.id
                first_tag_name = f.tag_name
                first_tag_slug = f.tag_name_slug

            first_tag_url = settings.BASE_URL + 'businesstag/' + first_tag_slug

            # Get related business listings
            rel_bl = get_related_bp(first_tag_name, id, 10)

            # Get business profile reviews, must convert to string first
            bp_reviews = str(get_bp_reviews(id))
            bp_reviews_data = load_bp_reviews(id)
            bp_tot_rates = str(sum_bp_reviews_rate(id))
            oa_rate = int(math_divide(int(bp_tot_rates), int(bp_reviews)))

            # Get business profile comments, must convert to string first
            bp_comments = str(get_bp_comments(id))
            bp_comments_data = load_bp_comments(id)

            # Get business inquiries
            bp_inquires = str(get_bp_inquiries(id))

            # Get bp comment form to display
            formComment = BPCommentForm()

            # Get bp review form to display
            formReview = BPReviewForm()

            # Get bp business inquiry form to display
            formInquiry = BPInquiryForm()

            # Get Featured image and override the default if found
            APP_URL_LOGO = settings.APP_URL_LOGO
            com_logo = settings.DEFAULT_COMPANY_LOGO
            is_com_logo_found = False

            if MediaLabUsedFiles.objects.filter(ref_id=id, src_type='BP'):
                feat_image = MediaLabUsedFiles.objects.filter(
                        ref_id=id, src_type='BP')

                for fi in feat_image:
                    orig_feat_image = MediaLab.objects.filter(id=fi.src_id)

                    for im in orig_feat_image:
                        APP_URL_LOGO = settings.BASE_URL + "media/" + str(im.file_name)
                        com_logo = str(im.file_name)
                        is_com_logo_found = True

            # Get business tags
            bt_tags = get_business_tags(id)

            return render(request, 'bp/bp.html',
                          {'title': meta_title,
                           'meta_desc': meta_desc + ' [' + str(id) + ']',
                           'content_title': company_name,
                           'content_desc': short_desc,
                           'company_name': company_name,
                           'address': address,
                           'office_hours': office_hours,
                           'short_desc': short_desc,
                           'tel_no': tel_no,
                           'fax_no': fax_no,
                           'website': website,
                           'about': about,
                           'is_active': is_active,
                           'created_by': created_by,
                           'created_date': created_date,
                           'modified_date': modified_date,
                           'bl_data': bl_data,
                           'rel_bl': rel_bl,
                           'id': id,
                           'slug': slugify(company_name),
                           'current_user_id': current_user.id,
                           'first_tag_id': first_tag_id,
                           'first_tag_name': first_tag_name,
                           'first_tag_slug': first_tag_slug,
                           'first_tag_url': first_tag_url,
                           'APP_URL_LOGO': APP_URL_LOGO,
                           'com_logo': com_logo,
                           'is_com_logo_found': is_com_logo_found,
                           'oa_rate': oa_rate,
                           'bp_reviews': bp_reviews,
                           'bp_reviews_data': bp_reviews_data,
                           'bp_tot_rates': bp_tot_rates,
                           'bp_comments': bp_comments,
                           'bp_comments_data': bp_comments_data,
                           'bp_inquires': bp_inquires,
                           'formComment': formComment,
                           'formReview': formReview,
                           'formInquiry': formInquiry,
                           'bt_tags': bt_tags})
        else:
            raise Http404()


def submitbp_comment_view(request):
    if request.method == 'POST':
        # Access business profile database
        with in_database(settings.APP_LABEL_BP, write=True):
            formComment = BPCommentForm(request.POST)
            BLID = request.POST.get('BLID')
            GET_USER_TZN = request.POST.get('GET_USER_TZN')

            if formComment.is_valid():

                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GRECAP_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post(settings.GRECAP_VERIFY_URL, data=data)
                result = r.json()
                ''' End reCAPTCHA validation '''

                if result['success']:

                    # Get match business profile data by id
                    bp_data = get_bl_by_id(BLID)
                    bp_slug = None
                    bp_email = None
                    bp_company_name = None
                    bp_profile_link = None
                    bp_created_by = 0

                    for bp in bp_data:
                        bp_slug = slugify(bp.company_name)
                        bp_email = bp.email
                        bp_company_name = bp.company_name
                        bp_created_by = bp.created_by
                        bp_profile_link = settings.BASE_URL + bp_slug + '-' + str(bp.id) + '-bp/'

                    # Save bp comment form data successfully
                    bpcmt = formComment.save(commit=False)
                    bpcmt.business_id = BLID
                    bpcmt.is_active = True
                    bpcmt.is_deleted = False

                    full_name = formComment.cleaned_data.get("full_name")
                    comment = formComment.cleaned_data.get("comment")

                    # Insert all <a href> tag with rel="nofollow" tag
                    r_nofollow = re.compile('<a (?![^>]*nofollow)')
                    s_nofollow = '<a rel="nofollow" '
                    comment_cleaned = r_nofollow.sub(s_nofollow, comment)

                    bpcmt.comment = comment_cleaned
                    bpcmt.save()  # Finally save the form data

                    # Submit new bp notifications
                    BusinessNotifications.objects.using(
                            settings.APP_LABEL_BP
                            ).create(user_id=bp_created_by,
                                     src_id=bpcmt.pk,  # Get the latest id
                                     business_id=BLID,
                                     src_type='CM')

                    # Call the celery task async
                    bp_comment_send_mail.delay(full_name, bp_email,
                                               comment, bp_profile_link,
                                               bp_company_name,
                                               GET_USER_TZN)

                    # Return some json response back to user
                    msg = """Your comment was sent successfully, thank you!"""
                    data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                    # Get the latest notification first row
                    nn = auto_notify_bp(bp_created_by)

                    # Auto notification using pubnub
                    for n in nn:
                        data["id"] = n['id']
                        data["notify_id"] = n['notify_id']
                        data["event_date"] = n['event_date']
                        data["src_id"] = n['src_id']
                        data["src_type"] = n['src_type']
                        data["url_info"] = n['url_info']
                        data["full_name"] = n['full_name']
                        data["message"] = n['message']
                        data["business_id"] = n['business_id']
                        data["company_name"] = n['company_name']
                        data["address"] = n['address']
                        data["short_desc"] = n['short_desc']

                else:

                    # Return some json response back to user
                    msg = """Invalid reCAPTCHA, please try again."""
                    data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            else:

                # Extract form.errors
                msg = None
                msg = [(k, v[0]) for k, v in formComment.errors.items()]
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            return JsonResponse(data)


def submitbp_review_view(request):
    if request.method == 'POST':
        # Access business profile database
        with in_database(settings.APP_LABEL_BP, write=True):
            formReview = BPReviewForm(request.POST)
            BLID = request.POST.get('BLID')
            GET_USER_TZN = request.POST.get('GET_USER_TZN')
            RATE = request.POST.get('rating')
            email = request.POST.get('email')

            if formReview.is_valid():

                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GRECAP_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post(settings.GRECAP_VERIFY_URL, data=data)
                result = r.json()
                ''' End reCAPTCHA validation '''

                if result['success']:

                    # Validate email address if exist from an email server.
                    is_email_real = is_email_valid(email)

                    if is_email_real:

                        # Get match business profile data by id
                        bp_data = get_bl_by_id(BLID)
                        bp_slug = None
                        bp_email = None
                        bp_company_name = None
                        bp_profile_link = None
                        bp_created_by = 0

                        for bp in bp_data:
                            bp_slug = slugify(bp.company_name)
                            bp_email = bp.email
                            bp_company_name = bp.company_name
                            bp_created_by = bp.created_by
                            bp_profile_link = settings.BASE_URL + bp_slug + '-' + str(bp.id) + '-bp/'

                        # Save bp review form data successfully
                        bprvw = formReview.save(commit=False)
                        bprvw.business_id = BLID
                        bprvw.is_active = True
                        bprvw.is_deleted = False
                        bprvw.rate = RATE

                        full_name = formReview.cleaned_data.get("full_name")
                        review = formReview.cleaned_data.get("review")

                        # Insert all <a href> tag with rel="nofollow" tag
                        r_nofollow = re.compile('<a (?![^>]*nofollow)')
                        s_nofollow = '<a rel="nofollow" '
                        review_cleaned = r_nofollow.sub(s_nofollow, review)

                        bprvw.review = review_cleaned
                        bprvw.save()  # Finally save the form data

                        # Submit new bp notifications
                        BusinessNotifications.objects.using(
                                settings.APP_LABEL_BP
                                ).create(user_id=bp_created_by,
                                         src_id=bprvw.pk,  # Get the latest id
                                         business_id=BLID,
                                         src_type='RV')

                        # Call the celery task async
                        bp_review_send_mail.delay(full_name, bp_email,
                                                  review, bp_profile_link,
                                                  bp_company_name, RATE,
                                                  GET_USER_TZN)

                        # Return some json response back to user
                        msg = """Your business review was sent successfully, thank you!"""
                        data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                        # Get the latest notification first row
                        nn = auto_notify_bp(bp_created_by)

                        # Auto notification using pubnub
                        for n in nn:
                            data["id"] = n['id']
                            data["notify_id"] = n['notify_id']
                            data["event_date"] = n['event_date']
                            data["src_id"] = n['src_id']
                            data["src_type"] = n['src_type']
                            data["url_info"] = n['url_info']
                            data["full_name"] = n['full_name']
                            data["message"] = n['message']
                            data["business_id"] = n['business_id']
                            data["company_name"] = n['company_name']
                            data["address"] = n['address']
                            data["short_desc"] = n['short_desc']
                    else:

                        # Return some json response back to user
                        msg = """Invalid or non-existed email address."""
                        data = dict_alert_msg('False', 'Oops, Invalid Email Address', msg, 'error')

                else:

                    # Return some json response back to user
                    msg = """Invalid reCAPTCHA, please try again."""
                    data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            else:

                # Extract form.errors
                msg = None
                msg = [(k, v[0]) for k, v in formReview.errors.items()]
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            return JsonResponse(data)


def submitbp_inquiry_view(request):
    if request.method == 'POST':
        # Access business profile database
        with in_database(settings.APP_LABEL_BP, write=True):
            formInquiry = BPInquiryForm(request.POST)
            BLID = request.POST.get('BLID')
            GET_USER_TZN = request.POST.get('GET_USER_TZN')
            email = request.POST.get('email')

            if formInquiry.is_valid():

                ''' Begin reCAPTCHA validation '''
                recaptcha_response = request.POST.get('g-recaptcha-response')
                data = {
                    'secret': settings.GRECAP_SECRET_KEY,
                    'response': recaptcha_response
                }
                r = requests.post(settings.GRECAP_VERIFY_URL, data=data)
                result = r.json()
                ''' End reCAPTCHA validation '''

                if result['success']:

                    # Validate email address if exist from an email server.
                    is_email_real = is_email_valid(email)

                    if is_email_real:

                        # Get match business profile data by id
                        bp_data = get_bl_by_id(BLID)
                        bp_slug = None
                        bp_email = None
                        bp_company_name = None
                        bp_profile_link = None
                        bp_created_by = 0

                        for bp in bp_data:
                            bp_slug = slugify(bp.company_name)
                            bp_email = bp.email
                            bp_company_name = bp.company_name
                            bp_created_by = bp.created_by
                            bp_profile_link = settings.BASE_URL + bp_slug + '-' + str(bp.id) + '-bp/'

                        # Save bp inquiry form data successfully
                        bpinq = formInquiry.save(commit=False)
                        bpinq.business_id = BLID
                        bpinq.is_active = True
                        bpinq.is_deleted = False

                        full_name = formInquiry.cleaned_data.get("full_name")
                        inquiry = formInquiry.cleaned_data.get("inquiry")
                        author_email = formInquiry.cleaned_data.get("email")
                        subject = formInquiry.cleaned_data.get("subject")

                        # Insert all <a href> tag with rel="nofollow" tag
                        r_nofollow = re.compile('<a (?![^>]*nofollow)')
                        s_nofollow = '<a rel="nofollow" '
                        inquiry_cleaned = r_nofollow.sub(s_nofollow, inquiry)

                        bpinq.inquiry = inquiry_cleaned
                        bpinq.save()  # Finally save the form data

                        # Submit new bp notifications
                        BusinessNotifications.objects.using(
                                settings.APP_LABEL_BP
                                ).create(user_id=bp_created_by,
                                         src_id=bpinq.pk,  # Get the latest id
                                         business_id=BLID,
                                         src_type='IN')

                        # Call the celery task async
                        bp_inquiry_send_mail.delay(full_name, bp_email,
                                                   inquiry, bp_profile_link,
                                                   bp_company_name, author_email,
                                                   subject, GET_USER_TZN)

                        # Return some json response back to user
                        msg = """Your business inquiry was sent successfully, thank you!"""
                        data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                        # Get the latest notification first row
                        nn = auto_notify_bp(bp_created_by)

                        # Auto notification using pubnub
                        for n in nn:
                            data["id"] = n['id']
                            data["notify_id"] = n['notify_id']
                            data["event_date"] = n['event_date']
                            data["src_id"] = n['src_id']
                            data["src_type"] = n['src_type']
                            data["url_info"] = n['url_info']
                            data["full_name"] = n['full_name']
                            data["message"] = n['message']
                            data["business_id"] = n['business_id']
                            data["company_name"] = n['company_name']
                            data["address"] = n['address']
                            data["short_desc"] = n['short_desc']
                    else:

                        # Return some json response back to user
                        msg = """Invalid or non-existed email address."""
                        data = dict_alert_msg('False', 'Oops, Invalid Email Address', msg, 'error')

                else:

                    # Return some json response back to user
                    msg = """Invalid reCAPTCHA, please try again."""
                    data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            else:

                # Extract form.errors
                msg = None
                msg = [(k, v[0]) for k, v in formInquiry.errors.items()]
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            return JsonResponse(data)


def searchbp_view(request):
    """Function to search common data inside dashboard."""
    if request.method == "GET":
        fsearch_top = request.GET.get('q')

        if fsearch_top and len(fsearch_top) >= settings.MIN_CHARS_SEARCH:
            # Search text inside business table
            link_query = Business.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                            id,
                            company_name,
                            address,
                            short_desc,
                            created_date
                            FROM minedbp_bp.bp_business
                            WHERE is_active = 1 AND is_deleted = 0 AND (company_name LIKE %s OR address LIKE %s OR short_desc LIKE %s OR about LIKE %s)
                            ORDER BY company_name ASC LIMIT 500""", ["%" + fsearch_top + "%", "%" + fsearch_top + "%", "%" + fsearch_top + "%", "%" + fsearch_top + "%"])

            link_lists = list(link_query)

            paginator = Paginator(link_lists, 50)  # Show 50 rows per page
            page = request.GET.get('page', 1)

            try:
                data_pages = paginator.page(page)
            except PageNotAnInteger:
                data_pages = paginator.page(1)
            except EmptyPage:
                data_pages = paginator.page(paginator.num_pages)

            # Get the index of the current page
            index = data_pages.number - 1  # edited to something easier without index
            max_index = len(paginator.page_range)
            start_index = index - 5 if index >= 5 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            page_range = list(paginator.page_range)[start_index:end_index]
            totRows = "{:,}".format(paginator.count)

            return render(request, 'bp/searchbp.html',
                          {
                              'title': 'Search Results for: ' + str(fsearch_top),
                              'meta_desc': 'These are the list of search results based on your search text criteria.',
                              'data_pages': data_pages,
                              'page_range': page_range,
                              'totRows': totRows,
                              'q': fsearch_top
                           })
        else:
            return redirect('emptysearch')


def business_tags_view(request, slug):
    """Renders all business links under this tagged."""
    if request.method == 'GET':

        # Get all the business profile under this tag name
        tag_bl_list = bp_tagged_bl_list(slug)

        # Get tag_name from a slug
        tag_name = ""
        tag_url = ""
        for t in tag_bl_list:
            tag_name = t.tag_name
            tag_url = t.tag_name_slug

        if tag_bl_list:
            paginator = Paginator(tag_bl_list, 50)
            page = request.GET.get('page', 1)

            try:
                bl_pages = paginator.page(page)
            except PageNotAnInteger:
                bl_pages = paginator.page(1)
            except EmptyPage:
                bl_pages = paginator.page(paginator.num_pages)

            # Get the index of the current page
            index = bl_pages.number - 1  # edited to something easier without index
            max_index = len(paginator.page_range)
            start_index = index - 5 if index >= 5 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            page_range = list(paginator.page_range)[start_index:end_index]

            totRows = "{:,}".format(paginator.count)
            cur_page_title = "[" + str(bl_pages.number) + "/" + str(bl_pages.paginator.num_pages) + "]"
            meta_title = "Newest '" + tag_name.title() + "' " + cur_page_title + " Business Tags - " + settings.APP_SHORTNAME
            meta_desc = """The complete list of """ + tag_name.title() + """ business tag, """ + cur_page_title + """, total of """ + str(totRows) + """ business profile
            under this business tag and if your business profile is not found, please
            submit your business profile absolutely free as always, and we will
            help your business propagate within our business networks - """ + settings.APP_SHORTNAME

            return render(request, 'bp/business_tags.html',
                          {'title': meta_title,
                           'meta_desc': meta_desc,
                           'tag_name': tag_name,
                           'tag_url': tag_url,
                           'slug': slug,
                           'bl_pages': bl_pages,
                           'page_range': page_range,
                           'totRows': totRows})
        else:
            raise Http404()


@login_required
def bp_reviews_view(request):
    """Renders the list of bp reviews page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user

        # Set session for the main left side bar active menu
        request.session['active_sidebar_menu'] = "reviews"

        fsearch = request.GET.get('q')

        if fsearch:
            # Get all reviews
            bl_data = get_bp_reviews_list(current_user.id, fsearch, 100)
        else:
            # Get all reviews
            bl_data = get_bp_reviews_list(current_user.id, "", 500)
            fsearch = ''

        paginator = Paginator(bl_data, 5)  # Show 5 rows per page
        page = request.GET.get('page', 1)

        try:
            data_pages = paginator.page(page)
        except PageNotAnInteger:
            data_pages = paginator.page(1)
        except EmptyPage:
            data_pages = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = data_pages.number - 1  # edited to something easier without index
        max_index = len(paginator.page_range)
        start_index = index - 2 if index >= 2 else 0
        end_index = index + 2 if index <= max_index - 2 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        totRows = "{:,}".format(paginator.count)

        return render(request, 'bp/reviews.html',
                      {
                          'title': 'Business Reviews',
                          'meta_desc': 'Manage your business reviews',
                          'bl_data': bl_data,
                          'data_pages': data_pages,
                          'page_range': page_range,
                          'totRows': totRows,
                          'q': fsearch
                       })


@login_required
def del_row_bp_review_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        # Current user logged in info
        current_user = request.user

        # Just update 'is_deleted=False' status of the row only
        BusinessReview.objects.using(settings.APP_LABEL_BP).filter(
                id=row_id).update(is_deleted=True,
                                  deleted_by=current_user.id,
                                  deleted_date=timezone.now())

        # Return some json response back to user
        msg = """Your deletion was successful, thank you!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        return JsonResponse(data)


@login_required
def reading_pane_bp_review_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        review_id = request.POST.get('review_id')

        # Get selected review data
        br_data = BusinessReview.objects.using(settings.APP_LABEL_BP).filter(
                id=review_id, is_active=True, is_deleted=False)

        business_id = 0
        full_name = ''
        email = ''
        rate = 0
        review = ''
        created_date = ''

        for b in br_data:
            business_id = b.business_id
            full_name = b.full_name
            email = b.email
            rate = b.rate
            review = b.review

            # Convert UTC datetime from db to user's local datetime.
            created_date = convertToLocalDateTime(b.created_date)

        # Get business profile info
        bp_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                id=business_id, is_active=True, is_deleted=False)

        company_name = ''
        url = ''

        for bp in bp_data:
            company_name = bp.company_name
            url = settings.BASE_URL + slugify(company_name) + "-" + str(business_id) + "-bp/"

        data["business_id"] = business_id
        data["url"] = url
        data["company_name"] = company_name
        data["full_name"] = full_name
        data["email"] = email
        data["rate"] = rate
        data["review"] = review
        data["created_date"] = created_date
        data["alert_type"] = 'success'

        return JsonResponse(data)


@login_required
def read_bp_review_view(request, id):
    """Renders the review reading page."""
    if request.method == "GET":

        # Current user logged in info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        # Check if valid access rights
        if is_super_user:
            bp_data = BusinessReview.objects.using(settings.APP_LABEL_BP).filter(
                    id=id, is_active=True, is_deleted=False)
        else:
            # Check first if the current user is the creator of the business listing.
            created_by = get_created_by_from_review_id(id)
            if current_user.id == created_by:
                bp_data = BusinessReview.objects.using(settings.APP_LABEL_BP).filter(
                        id=id, is_active=True, is_deleted=False)
            else:
                bp_data = None

        if bp_data:

            # Get the review data
            business_id = 0
            full_name = ''
            email = ''
            rate = ''
            review = ''
            created_date = ''

            for b in bp_data:
                business_id = b.business_id
                full_name = b.full_name
                email = b.email
                rate = b.rate
                review = b.review
                created_date = b.created_date

            # Get business profile data
            bl_data = get_bl_by_id(business_id)

            company_name = ''
            address = ''

            for l in bl_data:
                company_name = l.company_name
                address = l.address

            return render(request, 'bp/read_review.html',
                          {
                              'title': 'Read Review',
                              'meta_desc': 'Read review in full details.',
                              'business_id': business_id,
                              'full_name': full_name,
                              'email': email,
                              'rate': rate,
                              'review': review,
                              'created_date': created_date,
                              'company_name': company_name,
                              'address': address
                           })
        else:
            raise Http404()


@login_required
def inquiries_view(request):
    """Renders the manage inquiries page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user

        # Set session for the main left side bar active menu
        request.session['active_sidebar_menu'] = "inquiries"

        fsearch = request.GET.get('q')

        if fsearch:
            # Get all reviews
            bl_data = get_bp_inquiries_list(current_user.id, fsearch, 100)
        else:
            # Get all reviews
            bl_data = get_bp_inquiries_list(current_user.id, "", 500)
            fsearch = ''

        paginator = Paginator(bl_data, 5)  # Show 5 rows per page
        page = request.GET.get('page', 1)

        try:
            data_pages = paginator.page(page)
        except PageNotAnInteger:
            data_pages = paginator.page(1)
        except EmptyPage:
            data_pages = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = data_pages.number - 1  # edited to something easier without index
        max_index = len(paginator.page_range)
        start_index = index - 2 if index >= 2 else 0
        end_index = index + 2 if index <= max_index - 2 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        totRows = "{:,}".format(paginator.count)

        return render(request, 'bp/inquiries.html',
                      {
                          'title': 'Business Inquiries',
                          'meta_desc': 'Manage your business inquiries',
                          'bl_data': bl_data,
                          'data_pages': data_pages,
                          'page_range': page_range,
                          'totRows': totRows,
                          'q': fsearch
                       })


@login_required
def del_row_bp_inquiry_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        # Current user logged in info
        current_user = request.user

        # Just update 'is_deleted=False' status of the row only
        BusinessInquiry.objects.using(settings.APP_LABEL_BP).filter(
                id=row_id).update(is_deleted=True,
                                  deleted_by=current_user.id,
                                  deleted_date=timezone.now())

        # Return some json response back to user
        msg = """Your deletion was successful, thank you!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        return JsonResponse(data)


@login_required
def read_bp_inquiry_view(request, id):
    """Renders the inquiry reading page."""
    if request.method == "GET":

        # Current user logged in info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        # Check if valid access rights
        if is_super_user:
            bp_data = BusinessInquiry.objects.using(settings.APP_LABEL_BP).filter(
                    id=id, is_active=True, is_deleted=False)
        else:
            # Check first if the current user is the creator of the business listing.
            created_by = get_created_by_from_inquiry_id(id)
            if current_user.id == created_by:
                bp_data = BusinessInquiry.objects.using(settings.APP_LABEL_BP).filter(
                        id=id, is_active=True, is_deleted=False)
            else:
                bp_data = None

        if bp_data:

            # Get the inquiry data
            business_id = 0
            full_name = ''
            email = ''
            subject = ''
            inquiry = ''
            created_date = ''

            for b in bp_data:
                business_id = b.business_id
                full_name = b.full_name
                email = b.email
                subject = b.subject
                inquiry = b.inquiry
                created_date = b.created_date

            # Get business profile data
            bl_data = get_bl_by_id(business_id)

            company_name = ''
            address = ''

            for l in bl_data:
                company_name = l.company_name
                address = l.address

            return render(request, 'bp/read_inquiry.html',
                          {
                              'title': 'Read Inquiry',
                              'meta_desc': 'Read inquiry in full details.',
                              'business_id': business_id,
                              'full_name': full_name,
                              'email': email,
                              'subject': subject,
                              'inquiry': inquiry,
                              'created_date': created_date,
                              'company_name': company_name,
                              'address': address
                           })
        else:
            raise Http404()


@login_required
def reading_pane_bp_inquiry_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        inquiry_id = request.POST.get('inquiry_id')

        # Get selected review data
        br_data = BusinessInquiry.objects.using(settings.APP_LABEL_BP).filter(
                id=inquiry_id, is_active=True, is_deleted=False)

        business_id = 0
        full_name = ''
        email = ''
        subject = ''
        inquiry = ''
        created_date = ''

        for b in br_data:
            business_id = b.business_id
            full_name = b.full_name
            email = b.email
            subject = b.subject
            inquiry = b.inquiry

            # Convert UTC datetime from db to user's local datetime.
            created_date = convertToLocalDateTime(b.created_date)

        # Get business profile info
        bp_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                id=business_id, is_active=True, is_deleted=False)

        company_name = ''
        url = ''

        for bp in bp_data:
            company_name = bp.company_name
            url = settings.BASE_URL + slugify(company_name) + "-" + str(business_id) + "-bp/"

        data["business_id"] = business_id
        data["url"] = url
        data["company_name"] = company_name
        data["full_name"] = full_name
        data["email"] = email
        data["subject"] = subject
        data["inquiry"] = inquiry
        data["created_date"] = created_date
        data["alert_type"] = 'success'

        return JsonResponse(data)


@login_required
def comments_view(request):
    """Renders the manage inquiries page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user

        # Set session for the main left side bar active menu
        request.session['active_sidebar_menu'] = "comments"

        fsearch = request.GET.get('q')

        if fsearch:
            # Get all reviews
            bl_data = get_bp_comments_list(current_user.id, fsearch, 100)
        else:
            # Get all reviews
            bl_data = get_bp_comments_list(current_user.id, "", 500)
            fsearch = ''

        paginator = Paginator(bl_data, 5)  # Show 5 rows per page
        page = request.GET.get('page', 1)

        try:
            data_pages = paginator.page(page)
        except PageNotAnInteger:
            data_pages = paginator.page(1)
        except EmptyPage:
            data_pages = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = data_pages.number - 1  # edited to something easier without index
        max_index = len(paginator.page_range)
        start_index = index - 2 if index >= 2 else 0
        end_index = index + 2 if index <= max_index - 2 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        totRows = "{:,}".format(paginator.count)

        return render(request, 'bp/comments.html',
                      {
                          'title': 'Business Comments',
                          'meta_desc': 'Manage your business comments',
                          'bl_data': bl_data,
                          'data_pages': data_pages,
                          'page_range': page_range,
                          'totRows': totRows,
                          'q': fsearch
                       })


@login_required
def del_row_bp_comment_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        # Current user logged in info
        current_user = request.user

        # Just update 'is_deleted=False' status of the row only
        BusinessComment.objects.using(settings.APP_LABEL_BP).filter(
                id=row_id).update(is_deleted=True,
                                  deleted_by=current_user.id,
                                  deleted_date=timezone.now())

        # Return some json response back to user
        msg = """Your deletion was successful, thank you!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        return JsonResponse(data)


@login_required
def reading_pane_bp_comment_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        comment_id = request.POST.get('comment_id')

        # Get selected review data
        br_data = BusinessComment.objects.using(settings.APP_LABEL_BP).filter(
                id=comment_id, is_active=True, is_deleted=False)

        business_id = 0
        full_name = ''
        comment = ''
        created_date = ''

        for b in br_data:
            business_id = b.business_id
            full_name = b.full_name
            comment = b.comment

            # Convert UTC datetime from db to user's local datetime.
            created_date = convertToLocalDateTime(b.created_date)

        # Get business profile info
        bp_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                id=business_id, is_active=True, is_deleted=False)

        company_name = ''
        url = ''

        for bp in bp_data:
            company_name = bp.company_name
            url = settings.BASE_URL + slugify(company_name) + "-" + str(business_id) + "-bp/"

        data["business_id"] = business_id
        data["url"] = url
        data["company_name"] = company_name
        data["full_name"] = full_name
        data["comment"] = comment
        data["created_date"] = created_date
        data["alert_type"] = 'success'

        return JsonResponse(data)


@login_required
def read_bp_comment_view(request, id):
    """Renders the comment reading page."""
    if request.method == "GET":

        # Current user logged in info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        # Check if valid access rights
        if is_super_user:
            bp_data = BusinessComment.objects.using(settings.APP_LABEL_BP).filter(
                    id=id, is_active=True, is_deleted=False)
        else:
            # Check first if the current user is the creator of the business listing.
            created_by = get_created_by_from_comment_id(id)
            if current_user.id == created_by:
                bp_data = BusinessComment.objects.using(settings.APP_LABEL_BP).filter(
                        id=id, is_active=True, is_deleted=False)
            else:
                bp_data = None

        if bp_data:

            # Get the inquiry data
            business_id = 0
            full_name = ''
            comment = ''
            created_date = ''

            for b in bp_data:
                business_id = b.business_id
                full_name = b.full_name
                comment = b.comment
                created_date = b.created_date

            # Get business profile data
            bl_data = get_bl_by_id(business_id)

            company_name = ''
            address = ''

            for l in bl_data:
                company_name = l.company_name
                address = l.address

            return render(request, 'bp/read_comment.html',
                          {
                              'title': 'Read Comment',
                              'meta_desc': 'Read comment in full details.',
                              'business_id': business_id,
                              'full_name': full_name,
                              'comment': comment,
                              'created_date': created_date,
                              'company_name': company_name,
                              'address': address
                           })
        else:
            raise Http404()


def notify_me_bp(cur_user_id, num_rows):
    """Load latest notifications to the users belongs to the group."""
    # Load latest 10 notifications
    notify_data = Business.objects.raw("""SELECT
                                a.id,
                                a.src_type,
                                a.src_id,
                                DATE_FORMAT(a.event_date, "%%Y-%%m-%%d %%H:%%i:%%s") AS event_date_raw,
                                b.id as business_id,
                                b.company_name,
                                b.created_by,
                                c.notify_id
                                FROM minedbp_bp.bp_business_notification a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                LEFT JOIN minedbp_bp.bp_business_notification_read c ON c.notify_id = a.id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND b.created_by = %s
                                ORDER BY a.event_date DESC LIMIT %s""", [cur_user_id, num_rows])

    # Count latest un-read notifications and return only 1 record.
    notify_tot_unread = Business.objects.raw("""SELECT a.id, COUNT(CASE WHEN c.notify_id IS NULL THEN 0 END) AS mNotify_Tot_UnRead
                                         FROM minedbp_bp.bp_business_notification a
                                         JOIN minedbp_bp.bp_business b ON b.id = a.business_id AND b.created_by = %s
                                         LEFT JOIN minedbp_bp.bp_business_notification_read c ON c.notify_id = a.id
                                         WHERE c.notify_id IS NULL
                                         GROUP BY a.id""", [cur_user_id])

    notify_tot = len(list(notify_data))
    return [notify_data, notify_tot, notify_tot_unread]


@login_required
def notify_marked_sel_read_bp_view(request):
    """
    Function to insert record to 'notifications_read' for 'bp' app table as per
    user selected individual notification list.
    """
    data = dict()
    if request.method == "POST":
        # Get user info
        current_user = request.user

        # Access notifications database
        with in_database(settings.APP_LABEL_BP, write=True):
            notify_id = request.POST.get('notify_id')
            url_info = request.POST.get('url_info')

            if BusinessNotifications.objects.filter(id=notify_id).exists():
                if BusinessNotificationsRead.objects.filter(notify_id=notify_id,
                                                    user_id=current_user.id
                                                    ).exists():
                    # Already read exist, do nothing
                    data["notify_id"] = 'None'
                else:
                    # Insert new read status
                    BusinessNotificationsRead.objects.create(
                        notify_id=notify_id,
                        user_id=current_user.id
                    )
                    data["notify_id"] = notify_id

                data["url_to_go"] = url_info
                return JsonResponse(data)


def get_bp_notifications_view(cur_user_id):
    """Load latest notifications to the users belongs to the group."""
    # Load latest 10 notifications
    notify_data = Business.objects.raw("""SELECT
                                a.id,
                                a.src_type,
                                a.src_id,
                                DATE_FORMAT(a.event_date, "%%Y-%%m-%%d %%H:%%i:%%s") AS event_date_raw,
                                b.id as business_id,
                                b.company_name,
                                b.created_by,
                                c.notify_id
                                FROM minedbp_bp.bp_business_notification a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                LEFT JOIN minedbp_bp.bp_business_notification_read c ON c.notify_id = a.id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND b.created_by = %s
                                ORDER BY a.event_date DESC""", [cur_user_id])
    notify_list = list(notify_data)
    return notify_list


@login_required
def bpnotify_view(request):
    """
    Display all bp notifications
    """
    if request.method == "GET":
        # Get user info
        current_user = request.user

        # Execute celery task to marked all unread notifications as 'read'
        mark_all_read_notifications_bp.delay(current_user.id)

        # Notifications payload
        notify_data = get_bp_notifications_view(current_user.id)

        # Get the standard msg_code from settings
        msg_value = None
        notify_raw_dict = dict()
        notify_raw_list = []
        full_name = None
        url_info = ''

        for ms in notify_data:
            for key, value in settings.MSG_CODES_BP.items():
                if ms.src_type == key:
                    msg_value = value

                    # timeago in python library to get user's local time
                    now = datetime.now() + timedelta(seconds=60 * 3.4)
                    event_date = timeago.format(ms.event_date_raw, now)

                    business_id = 0
                    company_name = ""
                    address = ""
                    short_desc = ""

                    # compose the message
                    if key == 'CM' or key == 'IN' or key == 'RV':

                        # Get bp information
                        bp_data = get_bl_by_id(ms.business_id)

                        for b in bp_data:
                            business_id = b.id
                            company_name = b.company_name
                            address = b.address
                            short_desc = b.short_desc

                        # For comment notification
                        if key == 'CM':
                            msg_value = "Commented on your business profile."
                            for c in get_comment_data(ms.src_id):
                                full_name = c.full_name
                            url_info = settings.BASE_URL + 'comment/' + str(ms.src_id) + '/read'

                        # For inquiry notification
                        if key == 'IN':
                            msg_value = "Submitted business inquiry."
                            for i in get_inquiry_data(ms.src_id):
                                full_name = i.full_name
                            url_info = settings.BASE_URL + 'inquiry/' + str(ms.src_id) + '/read'

                        # For review notification
                        if key == 'RV':
                            msg_value = "Reviewed your business."
                            for r in get_review_data(ms.src_id):
                                full_name = r.full_name
                            url_info = settings.BASE_URL + 'review/' + str(ms.src_id) + '/read'

                    notify_raw_list.append({'id': ms.id,
                                            'notify_id': ms.notify_id,
                                            'event_date': event_date,
                                            'src_id': ms.src_id,
                                            'src_type': ms.src_type,
                                            'url_info': url_info,
                                            'full_name': full_name,
                                            'message': msg_value,
                                            'business_id': business_id,
                                            'company_name': company_name,
                                            'address': address,
                                            'short_desc': short_desc})
        notify_raw_dict = notify_raw_list

        paginator = Paginator(notify_raw_dict, 25)  # Show 25 rows per page
        page = request.GET.get('page', 1)

        try:
            data_pages = paginator.page(page)
        except PageNotAnInteger:
            data_pages = paginator.page(1)
        except EmptyPage:
            data_pages = paginator.page(paginator.num_pages)

        # Get the index of the current page
        index = data_pages.number - 1  # edited to something easier without index
        max_index = len(paginator.page_range)
        start_index = index - 5 if index >= 5 else 0
        end_index = index + 5 if index <= max_index - 5 else max_index
        page_range = list(paginator.page_range)[start_index:end_index]
        totRows = "{:,}".format(paginator.count)

        return render(request, 'bp/bp_notifications.html',
                      {
                          'title': 'Notifications',
                          'meta_desc': 'Display all previous notifications.',
                          'data_pages': data_pages,
                          'page_range': page_range,
                          'totRows': totRows
                       })


def auto_notify_bp(src_user_id):
    """Get the newest notification to feed pubnub api."""
    # Notifications payload, latest first row
    notify_data, notify_tot, notify_tot_unread = notify_me_bp(
        src_user_id, 1)

    # Get the standard msg_code from settings
    msg_value = None
    notify_raw_dict = dict()
    notify_raw_list = []
    full_name = None
    url_info = ''

    for ms in notify_data:
        for key, value in settings.MSG_CODES_BP.items():
            if ms.src_type == key:
                msg_value = value

                # timeago in python library to get user's local time
                now = datetime.now() + timedelta(seconds=60 * 3.4)
                event_date = timeago.format(ms.event_date_raw, now)

                business_id = 0
                company_name = ""
                address = ""
                short_desc = ""

                # compose the message
                if key == 'CM' or key == 'IN' or key == 'RV':

                    # Get bp information
                    bp_data = get_bl_by_id(ms.business_id)

                    for b in bp_data:
                        business_id = b.id
                        company_name = b.company_name
                        address = b.address
                        short_desc = b.short_desc

                    # For comment notification
                    if key == 'CM':
                        msg_value = "Commented on your business profile."
                        for c in get_comment_data(ms.src_id):
                            full_name = c.full_name
                        url_info = settings.BASE_URL + 'comment/' + str(ms.src_id) + '/read'

                    # For inquiry notification
                    if key == 'IN':
                        msg_value = "Submitted business inquiry."
                        for i in get_inquiry_data(ms.src_id):
                            full_name = i.full_name
                        url_info = settings.BASE_URL + 'inquiry/' + str(ms.src_id) + '/read'

                    # For review notification
                    if key == 'RV':
                        msg_value = "Reviewed your business."
                        for r in get_review_data(ms.src_id):
                            full_name = r.full_name
                        url_info = settings.BASE_URL + 'review/' + str(ms.src_id) + '/read'

                notify_raw_list.append({'id': ms.id,
                                        'notify_id': ms.notify_id,
                                        'event_date': event_date,
                                        'src_id': ms.src_id,
                                        'src_type': ms.src_type,
                                        'url_info': url_info,
                                        'full_name': full_name,
                                        'message': msg_value,
                                        'business_id': business_id,
                                        'company_name': company_name,
                                        'address': address,
                                        'short_desc': short_desc})
    notify_raw_dict = notify_raw_list

    return notify_raw_dict


@login_required
def del_logo_view(request):
    """To delete logo from change bl form."""
    data = dict()
    if request.method == 'POST':
        image_id = request.POST.get('image_id')

        # Current user logged in info
        current_user = request.user

        # Just update 'is_deleted=False' status of the row only
        MediaLabUsedFiles.objects.filter(src_id=image_id, src_type=settings.REF_USED_BP).delete()

        # Return some json response back to user
        msg = """Your deletion was successful, thank you!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        data["default_logo"] = settings.DEFAULT_COMPANY_LOGO

        return JsonResponse(data)


def old_url_about_view(request):
    """
    Auto redirect old 'about' url to the new url.
    """
    if request.method == "GET":
        return redirect('about', permanent=True)


def old_url_contact_us_view(request):
    """
    Auto redirect old 'contact us' url to the new url.
    """
    if request.method == "GET":
        return redirect('contactus', permanent=True)


def old_url_advert_view(request):
    """
    Auto redirect old 'advertise' url to the new url.
    """
    if request.method == "GET":
        return redirect('advertise', permanent=True)


def old_url_register_view(request):
    """
    Auto redirect old 'register' url to the new url.
    """
    if request.method == "GET":
        return redirect('register', permanent=True)


def old_url_login_view(request):
    """
    Auto redirect old 'login' url to the new url.
    """
    if request.method == "GET":
        return redirect('login', permanent=True)


def old_url_forgot_view(request):
    """
    Auto redirect old 'login' url to the new url.
    """
    if request.method == "GET":
        return redirect('password_reset', permanent=True)


def old_url_mybusiness_view(request):
    """Auto redirect old 'login' url to the new url."""
    if request.method == "GET":
        return redirect('home', permanent=True)


def old_url_co_view(request, id, slug):
    """Permanent redirect 301 from old mybusiness url, e.g."""
    if request.method == 'GET':
        new_co_url = settings.BASE_URL + slug + "-" + str(id) + "-bp"
        return redirect(new_co_url, permanent=True)


def old_url_category_view(request, id, slug):
    """Permanent redirect 301 from old mybusiness url, e.g."""
    if request.method == 'GET':
        new_cat_url = settings.BASE_URL + "businesstag/" + slug
        return redirect(new_cat_url, permanent=True)


def mail_view(request):
    """Permanent redirect 301 for mail"""
    if request.method == 'GET':
        mail_url = "https://cs14.webhostbox.net:2096"
        return redirect(mail_url, permanent=True)


@login_required
def copy_bp_view(request):
    """Renders the copy of existing business listing data."""
    data = dict()
    if request.method == 'POST':
        business_id = request.POST.get('business_id')

        # Get user info
        current_user = request.user
        is_super_user = get_is_super_user(current_user.id)

        # Validate if superuser
        if is_super_user:
            # Get existing bl data
            bl_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                    id=business_id, is_deleted=False)

            if bl_data:

                for b in bl_data:
                    # Copy existing business listing
                    Business.objects.using(settings.APP_LABEL_BP).create(
                            company_name=b.company_name,
                            address=b.address,
                            tel_no=b.tel_no,
                            fax_no=b.fax_no,
                            email=b.email,
                            website=b.website,
                            is_website_no_follow=b.is_website_no_follow,
                            office_hours=b.office_hours,
                            short_desc=b.short_desc,
                            about=b.about,
                            is_active=False,
                            created_by=current_user.id,
                            is_deleted=False)

                    # MUST GET THE LATEST INSERTED ROW ID
                    new_bp = Business.objects.using(settings.APP_LABEL_BP).order_by('-id')[:1]
                    new_business_id = 0
                    for n in new_bp:
                        new_business_id = n.id

                    # Get existing bl data
                    tg_data = BusinessTag.objects.using(settings.APP_LABEL_BP).filter(
                            business_id=b.id, is_active=True, is_deleted=False)

                    for t in tg_data:
                        # Copy business tags
                        BusinessTag.objects.using(settings.APP_LABEL_BP).create(
                                business_id=new_business_id,
                                tag_name=t.tag_name,
                                tag_name_slug=t.tag_name_slug,
                                is_active=True,
                                created_by=current_user.id,
                                is_deleted=False)

                    # Get existing MediaLabUsedFiles data for existing logo
                    com_logo = MediaLabUsedFiles.objects.filter(ref_id=business_id)

                    for c in com_logo:
                        # Copy company logo
                        MediaLabUsedFiles.objects.create(
                                src_id=c.src_id,
                                src_type=c.src_type,
                                ref_id=new_business_id,
                                used_by_user_id=c.used_by_user_id)

                # Return some json response back to user
                msg = """Your copy operation was successful, thank you!"""
                data = dict_alert_msg('True', 'Success!', msg, 'success')

                data["new_business_id"] = new_business_id

            else:
                # Return some json response back to user
                msg = """Business listing data not existed."""
                data = dict_alert_msg('True', 'Make sure you copied the existing data!', msg, 'error')
        else:
            # Return some json response back to user
            msg = """Access is Denied!"""
            data = dict_alert_msg('True', "Your're not allowed to copy this data.", msg, 'error')

        return JsonResponse(data)
