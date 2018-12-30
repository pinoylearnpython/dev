from django.conf import settings
from django.db.models import Sum
from django.db.models import F, Sum, Count
from datetime import datetime, timedelta, date
import pytz

# Call all bp app properties
from bp.models import (Business, BusinessTag, BusinessReview, BusinessComment,
                       BusinessInquiry)

# Call all myroot app properties
from myroot.common import (get_user_membership_type, get_membership_by_code)

# Call medialab properties
from medialab.models import (MediaLab, MediaLabUsedFiles)


def get_bl_by_id(bp_id):
    """
    Function to get business listing data filtered by 'id'
    """
    bl_data = Business.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=bp_id)
    return bl_data


def get_bl_by_id_dashboard(ref_id):
    """
    Function to get link data filtered by 'id'
    """
    bl_data = Business.objects.using(settings.APP_LABEL_BP).filter(
            is_deleted=False, id=ref_id)
    return bl_data


def get_bl_by_user_id_dashboard(user_id, num_rows, is_super_user):
    """
    Function to get business listings data filtered by 'user_id'
    either 'is_active' is True or False
    """
    if is_super_user:
        bl_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                is_deleted=False
                ).order_by('-id')[:num_rows]
    else:
        bl_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                is_deleted=False, created_by=user_id
                ).order_by('-id')[:num_rows]
    return bl_data


def get_bp_tags(business_id):
    """
    Function to get business tags based on bp_id
    """
    tag = BusinessTag.objects.using(settings.APP_LABEL_BP).filter(
            business_id=business_id, is_active=True, is_deleted=False)
    return tag


def get_bp_logo(business_id, user_id, is_super_user):
    """
    Function to get bp logo filtered by 'business_id'
    """
    # Get bp logo
    if is_super_user:
        feat_image = MediaLabUsedFiles.objects.using('default').filter(
            ref_id=business_id,
            src_type=settings.REF_USED_BP)
    else:
        feat_image = MediaLabUsedFiles.objects.using('default').filter(
            used_by_user_id=user_id,
            ref_id=business_id,
            src_type=settings.REF_USED_BP)

    featured_image = settings.DEFAULT_COMPANY_LOGO
    is_featured_image_found = False
    image_id = 0

    for a in feat_image:
        src_id = a.src_id

        if is_super_user:
            # Get MediaLab image file_name
            img = MediaLab.objects.using('default').filter(
                    id=src_id)
        else:
            # Get MediaLab image file_name
            img = MediaLab.objects.using('default').filter(
                    id=src_id, uploaded_by=user_id)

        for i in img:
            featured_image = i.file_name
            is_featured_image_found = True
            image_id = i.id

    return featured_image, is_featured_image_found, image_id


def get_related_bp(tag_name, business_id, num_rows):
    """
    Function to get related bp filtered by 'tag_name'
    either 'is_active' is True or False
    """
    bl_list = Business.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                            a.id,
                            a.company_name,
                            a.address,
                            a.created_by,
                            a.created_date,
                            b.id as user_id,
                            b.username,
                            CONCAT(b.first_name, ' ', b.last_name) AS user_full_name,
                            c.tag_name
                            FROM minedbp_bp.bp_business a
                            LEFT JOIN minedbp_user.auth_user b ON b.id = a.created_by
                            LEFT JOIN minedbp_bp.bp_business_tag c ON c.business_id = a.id
                            WHERE a.is_active = 1 AND a.is_deleted = 0 AND b.is_active = 1 AND c.is_active = 1 AND c.is_deleted = 0
                            AND c.tag_name = %s AND a.id <> %s ORDER BY a.id DESC LIMIT %s""", [tag_name, business_id, num_rows])
    bl_lists = list(bl_list)
    return bl_lists


def get_bp_reviews(business_id):
    """
    Function to get total number of reviews for a certain business profile
    filtered by business_id
    """
    bp_reviews = BusinessReview.objects.using(
            settings.APP_LABEL_BP).filter(
                    business_id=business_id, is_active=True,
                    is_deleted=False).count()
    return bp_reviews


def load_bp_reviews(business_id):
    """
    Function to load all the latest business profile reviews for
    better seo technique no matter how long the page is.
    """
    bp_review = BusinessReview.objects.using(
            settings.APP_LABEL_BP).filter(
                    is_active=True, is_deleted=False,
                    business_id=business_id).order_by('-created_date')
    return bp_review


def sum_bp_reviews_rate(business_id):
    """
    Function to get the total sum of business reviews rating.
    """
    bp_rate_sum = BusinessReview.objects.using(
            settings.APP_LABEL_BP).filter(
                    is_active=True, is_deleted=False, business_id=business_id
                    ).aggregate(sum=Sum('rate'))['sum']

    if bp_rate_sum is None:
        bp_rate_sum = 0

    return bp_rate_sum


def get_bp_comments(business_id):
    """
    Function to get total comments for a certain business profile
    filtered by business_id
    """
    bp_comments = BusinessComment.objects.using(
            settings.APP_LABEL_BP).filter(
                    business_id=business_id, is_active=True,
                    is_deleted=False).count()
    return bp_comments


def load_bp_comments(business_id):
    """
    Function to load all the latest business profile comments for
    better seo technique no matter how long the page is.
    """
    bp_cmt = BusinessComment.objects.using(
            settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, business_id=business_id
            ).order_by('-created_date')
    return bp_cmt


def get_bp_inquiries(business_id):
    """
    Function to get total number of business inquiries for a certain business
    profile filtered by business_id
    """
    bp_reviews = BusinessInquiry.objects.using(
            settings.APP_LABEL_BP).filter(
                    business_id=business_id, is_active=True,
                    is_deleted=False).count()
    return bp_reviews


def count_bp(created_by, is_super_user):
    """
    Function to get user's total number of business profile
    """
    if is_super_user:
        num_bp = Business.objects.using(
                settings.APP_LABEL_BP).filter(
                        is_deleted=False).count()
    else:
        num_bp = Business.objects.using(
                settings.APP_LABEL_BP).filter(
                        created_by=created_by, is_deleted=False).count()

    return num_bp


def bp_tagged_bl_list(tag_name_slug):
    """Function to fetch sub business profile filtered by tag_id"""
    bp_list = BusinessTag.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                a.id,
                                a.tag_name,
                                b.id as business_id,
                                b.company_name,
                                b.address,
                                b.short_desc
                                FROM minedbp_bp.bp_business_tag a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1 AND a.is_deleted = 0 AND a.tag_name_slug = %s ORDER BY b.company_name ASC""", [tag_name_slug])
    bl_data = list(bp_list)
    return bl_data


def count_bp_inquiries(user_id, is_super_user):
    """
    Function to get total number of business inquiries
    """
    if is_super_user:
        bp_list = BusinessInquiry.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    1 as id, COUNT(*) as num_bp_inquiries
                                    FROM minedbp_bp.bp_business_inquiry a
                                    LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                    WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                    AND a.is_deleted = 0""")
    else:
        bp_list = BusinessInquiry.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    1 as id, COUNT(*) as num_bp_inquiries
                                    FROM minedbp_bp.bp_business_inquiry a
                                    LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                    WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                    AND a.is_deleted = 0 AND b.created_by = %s""", [user_id])
    bl_data = list(bp_list)
    return bl_data


def get_bp_reviews_list(user_id, search_text, num_rows):
    """
    Function to get business reviews data filtered by 'user_id' and exclude
    'is_deleted=True' and 'is_active=False'
    """
    bp_list = BusinessReview.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                a.id,
                                a.full_name,
                                a.rate,
                                a.email,
                                a.review,
                                a.created_date,
                                b.id as business_id,
                                b.company_name,
                                b.address,
                                b.short_desc,
                                b.created_by
                                FROM minedbp_bp.bp_business_review a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                AND a.is_deleted = 0 AND b.created_by = %s
                                AND (a.full_name LIKE %s OR a.email LIKE %s OR a.review LIKE %s)
                                ORDER BY a.id DESC LIMIT %s""", [user_id, '%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%', num_rows])
    bl_data = list(bp_list)
    return bl_data


def get_bp_inquires(user_id, num_rows):
    """
    Function to get business inquiries data filtered by 'user_id' and exclude
    'is_deleted=True' and 'is_active=False'
    """
    bp_list = BusinessTag.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                a.id,
                                a.full_name,
                                a.subject,
                                a.email,
                                a.created_date,
                                b.id as business_id,
                                b.company_name,
                                b.address,
                                b.short_desc,
                                b.created_by
                                FROM minedbp_bp.bp_business_inquiry a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                AND a.is_deleted = 0 AND b.created_by = %s ORDER BY a.id DESC LIMIT %s""", [user_id, num_rows])
    bl_data = list(bp_list)
    return bl_data


def get_bp_inquiries_list(user_id, search_text, num_rows):
    """
    Function to get business inquiries data filtered by 'user_id' and exclude
    'is_deleted=True' and 'is_active=False'
    """
    bp_list = BusinessInquiry.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                a.id,
                                a.full_name,
                                a.email,
                                a.subject,
                                a.inquiry,
                                a.created_date,
                                b.id as business_id,
                                b.company_name,
                                b.address,
                                b.short_desc,
                                b.created_by
                                FROM minedbp_bp.bp_business_inquiry a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                AND a.is_deleted = 0 AND b.created_by = %s
                                AND (a.full_name LIKE %s OR a.email LIKE %s OR a.subject LIKE %s OR a.inquiry LIKE %s)
                                ORDER BY a.id DESC LIMIT %s""", [user_id, '%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%', '%' + search_text + '%', num_rows])
    bl_data = list(bp_list)
    return bl_data


def get_bp_comments_list(user_id, search_text, num_rows):
    """
    Function to get business inquiries data filtered by 'user_id' and exclude
    'is_deleted=True' and 'is_active=False'
    """
    bp_list = BusinessComment.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                a.id,
                                a.full_name,
                                a.comment,
                                a.created_date,
                                b.id as business_id,
                                b.company_name,
                                b.address,
                                b.short_desc,
                                b.created_by
                                FROM minedbp_bp.bp_business_comment a
                                LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                AND a.is_deleted = 0 AND b.created_by = %s
                                AND (a.full_name LIKE %s OR a.comment LIKE %s)
                                ORDER BY a.id DESC LIMIT %s""", [user_id, '%' + search_text + '%', '%' + search_text + '%', num_rows])
    bl_data = list(bp_list)
    return bl_data


def count_bp_reviews(user_id, is_super_user):
    """
    Function to get total number of business reviews
    """
    if is_super_user:
        bp_list = BusinessReview.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    1 as id, COUNT(*) as num_bp_reviews
                                    FROM minedbp_bp.bp_business_review a
                                    LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                    WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                    AND a.is_deleted = 0""")
    else:
        bp_list = BusinessReview.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    1 as id, COUNT(*) as num_bp_reviews
                                    FROM minedbp_bp.bp_business_review a
                                    LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                    WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                    AND a.is_deleted = 0 AND b.created_by = %s""", [user_id])
    bl_data = list(bp_list)
    return bl_data


def count_bp_comments(user_id, is_super_user):
    """
    Function to get total number of business comments
    """
    if is_super_user:
        bp_list = BusinessComment.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    1 as id, COUNT(*) as num_bp_comments
                                    FROM minedbp_bp.bp_business_comment a
                                    LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                    WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                    AND a.is_deleted = 0""")
    else:
        bp_list = BusinessComment.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    1 as id, COUNT(*) as num_bp_comments
                                    FROM minedbp_bp.bp_business_comment a
                                    LEFT JOIN minedbp_bp.bp_business b ON b.id = a.business_id
                                    WHERE b.is_active = 1 AND b.is_deleted = 0 AND a.is_active = 1
                                    AND a.is_deleted = 0 AND b.created_by = %s""", [user_id])
    bl_data = list(bp_list)
    return bl_data


def get_comment_data(id):
    """
    Function to get business comment data filtered by 'id'
    """
    bl_data = BusinessComment.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=id)
    return bl_data


def get_inquiry_data(id):
    """
    Function to get business inquiry data filtered by 'id'
    """
    bl_data = BusinessInquiry.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=id)
    return bl_data


def get_review_data(id):
    """
    Function to get business review data filtered by 'id'
    """
    bl_data = BusinessReview.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=id)
    return bl_data


def get_business_tags(business_id):
    """Function to fetch business tags filtered by business_id"""
    bp_tags = BusinessTag.objects.using(settings.APP_LABEL_BP).raw("""SELECT a.id,
                                b.id as tag_id,
                                b.business_id,
                                b.tag_name
                                FROM minedbp_bp.bp_business a
                                LEFT JOIN minedbp_bp.bp_business_tag b ON a.id = b.business_id
                                WHERE a.id = %s AND a.is_active = 1 AND a.is_deleted = 0 AND b.is_active = 1
                                AND b.is_deleted = 0 ORDER BY b.id ASC""", [business_id])
    bp_tags_list = list(bp_tags)
    return bp_tags_list


def get_submitted_bp_by_user(user_id, mDays):
    """
    Function to get all submitted business listing filtered by 'created_by' and
    'created_date' either 'Draft' or 'Publish'
    """
    num_days = int(mDays)
    today_date = str(date.today())

    # Format date
    date_format = '%Y-%m-%d'

    unaware_start_date = datetime.strptime(today_date, date_format)
    aware_start_date = pytz.utc.localize(unaware_start_date) - timedelta(days=num_days)

    # +1 day when use BETWEEN statement in mysql query and django use the
    # __range as equivalent to BETWEEN statement.
    unaware_end_date = datetime.strptime(today_date, date_format)
    aware_end_date = pytz.utc.localize(unaware_end_date) + timedelta(days=1)

    bp_data = Business.objects.using(settings.APP_LABEL_BP).filter(
            is_deleted=False, created_by=user_id,
            created_date__range=(aware_start_date, aware_end_date))
    return bp_data


def is_bp_post_reach_limit(user_id):
    """Function to check if submission of new business listing reach to its
    allowed limit"""
    mem_code = get_user_membership_type(user_id)
    membership_code = ""
    for m in mem_code:
        membership_code = m.membership_code

    # Check number of max post
    mp = get_membership_by_code(membership_code)
    max_post = 0
    for p in mp:
        max_post = p.max_post

    # Reset important variables
    check_is_post_reach_limit = False
    get_posts = 0
    num_post = 0
    testC = ''

    # Check if Member or not
    if settings.MEM_CODE == membership_code:

        # Free members can post once a week only
        get_posts = get_submitted_bp_by_user(user_id, 7)
        num_post = get_posts.count()

    else:

        # All Paid members here must check number of post 'Daily'
        get_posts = get_submitted_bp_by_user(user_id, 1)
        num_post = get_posts.count()

    # Count number of submitted business listing based on the 'created_date' either
    # 'Draft' or 'Publish' status
    # Now match num_post vs max_post
    # max_post = 0 means, Unlimited posts
    if max_post == 0:
        check_is_post_reach_limit = False
    else:
        if num_post >= max_post:
            check_is_post_reach_limit = True

    return check_is_post_reach_limit


def get_latest_bp(num_rows1, num_rows2):
    """Function to get latest business links data with limited rows"""
    bl_list = Business.objects.using(settings.APP_LABEL_BP).raw("""SELECT
                                    a.id,
                                    a.company_name,
                                    a.short_desc,
                                    a.address,
                                    a.created_by,
                                    a.created_date,
                                    b.id as user_id,
                                    b.username,
                                    CONCAT(b.first_name, ' ', b.last_name) AS user_full_name,
                                    f.file_name as media_file_name
                                    FROM minedbp_bp.bp_business a
                                    LEFT JOIN minedbp_user.auth_user b ON b.id = a.created_by
                                    LEFT JOIN minedbp_user.medialab_used_files e ON e.used_by_user_id = a.created_by AND e.src_type = 'BP' AND e.ref_id = a.id
                                    LEFT JOIN minedbp_user.medialab f ON f.uploaded_by = f.uploaded_by AND f.id = e.src_id
                                    WHERE a.is_active = 1 AND a.is_deleted = 0 AND b.is_active = 1
                                    ORDER BY a.id DESC LIMIT %s, %s""", [num_rows1, num_rows2])
    bl_lists = list(bl_list)
    return bl_lists


def get_created_by_from_inquiry_id(inquiry_id):
    """
    Function business_id from inquiry data.
    """
    bl_data = BusinessInquiry.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=inquiry_id)

    business_id = 0
    created_by = 0

    for b in bl_data:
        business_id = b.business_id

        # Get the creator id
        creator_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                is_active=True, is_deleted=False, id=business_id)

        for c in creator_data:
            created_by = c.created_by

    return created_by


def get_created_by_from_review_id(review_id):
    """
    Function business_id from review data.
    """
    bl_data = BusinessReview.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=review_id)

    business_id = 0
    created_by = 0

    for b in bl_data:
        business_id = b.business_id

        # Get the creator id
        creator_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                is_active=True, is_deleted=False, id=business_id)

        for c in creator_data:
            created_by = c.created_by

    return created_by


def get_created_by_from_comment_id(comment_id):
    """
    Function business_id from comment data.
    """
    bl_data = BusinessComment.objects.using(settings.APP_LABEL_BP).filter(
            is_active=True, is_deleted=False, id=comment_id)

    business_id = 0
    created_by = 0

    for b in bl_data:
        business_id = b.business_id

        # Get the creator id
        creator_data = Business.objects.using(settings.APP_LABEL_BP).filter(
                is_active=True, is_deleted=False, id=business_id)

        for c in creator_data:
            created_by = c.created_by

    return created_by
