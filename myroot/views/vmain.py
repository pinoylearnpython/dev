from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.http import Http404
from django.utils.text import slugify
from django.db.models import Q
import json
import pytz
import arrow
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect

# Django Auth System
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
import requests

# Call myroot properties
from myroot.forms.fmain import (Basic_CRUD_Create_Form, SignUpForm,
                                LoginAuthenticationForm, PasswordResetForm,
                                PasswordResetConfirmForm)

from myroot.views.vfunctions import (dict_alert_msg, convert_to_local_datetime,
                                     is_email_valid, is_password_valid,
                                     is_username_valid)

from myroot.models import ContactUs, SiteConfig
from myroot.tokens import account_activation_token

# For Celery related custom functions
from myroot.views.tasks import contactus_send_mail
from myroot.views.vemail import do_send_email

# All the common functions to be loaded here.
from myroot.common import (get_contact_us_list, is_contact_us_id_exist)


def hello_world_view(request):
    """Renders the Hello World page."""
    if request.method == 'GET':
        return render(request, 'myroot/hello_world.html',
                      {'title': 'Hello World!',
                       'meta_desc': "The complete step-by-step guide in displaying Hello World using Django Template with NGINX guide to set up a new website from scratch.",
                       'BASE_URL': settings.BASE_URL,
                       'mtest': settings.STATIC_ROOT})


def basic_crud_create_view(request):
    """Renders the basic crud create operation."""
    if request.method == 'GET':

        # Get contact us form to display
        form = Basic_CRUD_Create_Form()
        return render(request, 'myroot/basic_crud_create.html',
                      {'form': form,
                       'title': "Django Basic CRUD: CREATE New Row with Actual Example",
                       'meta_desc': """Learn Django basic CRUD to create a new rows and store it on dev_contact_us database table - """ + settings.SITE_FULL_NAME})

    data = dict()
    if request.method == 'POST':
        # Get the form data
        form = Basic_CRUD_Create_Form(request.POST)

        if form.is_valid():
            form.save()  # insert new row

            # Return some json response back to the user
            msg = """ Your data has been inserted successfully, thank you! """
            data = dict_alert_msg('True', 'Awesome!', msg, 'success')

        else:

            # Extract form.errors
            msg = None
            msg = [(k, v[0]) for k, v in form.errors.items()]
            data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

        return JsonResponse(data)


def basic_crud_list_view(request):
    """
    This is the main Django Template to display the recent Basic CRUD
    table rows that you can manage using DataTable object.
    """
    if request.method == "GET":

        db_data = ContactUs.objects.filter(
                is_deleted=False
                ).order_by('-id')[:50]  # fetch the latest 50 rows

        return render(request, 'myroot/basic_crud_list.html',
                      {
                          'title': 'Django Basic CRUD: Manage Table Rows using DataTables',
                          'meta_desc': 'Learn how to display the database table rows using DataTables.',
                          'db_data': db_data
                       })


def basic_crud_del_row_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        # Just update 'is_deleted=False' status of the row only
        ContactUs.objects.filter(
                id=row_id).update(is_deleted=True,
                                  deleted_by=1,
                                  deleted_date=timezone.now())

        # Return some json response back to the user
        msg = """Poof! Your selected data row has been deleted!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        return JsonResponse(data)


def basic_crud_dynamic_public_page_view(request, slug, id):
    """Renders the dynamic public page."""
    if request.method == 'GET':

        # Get match table row by id
        db_data = ContactUs.objects.filter(is_deleted=False, id=id)

        # Use for loop to get the filtered row from a database table
        meta_title = ""
        meta_desc = ""

        for d in db_data:
            meta_title = d.full_name
            meta_desc = d.subject

        if db_data.count():
            return render(request, 'myroot/basic_django_dynamic_public_page.html',
                          {'title': meta_title + " - Django Basic Dynamic Public Page" + ' [' + str(id) + ']',
                           'meta_desc': meta_desc + ' [' + str(id) + ']',
                           'db_data': db_data})
        else:
            raise Http404()


def basic_crud_update_row_view(request, id):
    """Renders the Django edit form page and execute the update statement."""
    if request.method == "GET":

        # Get the selected row information
        db_data = ContactUs.objects.filter(id=id, is_deleted=False)

        if db_data:

            # Edit form data
            edit_data = ContactUs.objects.get(id=id, is_deleted=False)
            formEdit = Basic_CRUD_Create_Form(instance=edit_data)

            return render(request, 'myroot/basic_crud_update.html',
                          {
                              'title': 'Django Basic CRUD Update Statement',
                              'meta_desc': 'This is the actual example on Django basic crud which is the update statement.',
                              'id': id,
                              'formEdit': formEdit
                           })
        else:
            raise Http404()

    data = dict()
    if request.method == "POST":

        # Get the  form modified data
        form_edit = Basic_CRUD_Create_Form(request.POST)
        id = request.POST.get('id')

        if form_edit.is_valid():

            # Check if the row still not deleted
            if ContactUs.objects.filter(id=id, is_deleted=False).exists():

                # Get the form edit instance
                update_data = ContactUs.objects.get(id=id, is_deleted=False)

                # Now, supply the form data to an instance
                form_edit = Basic_CRUD_Create_Form(request.POST, instance=update_data)
                form_edit.save()  # Finally save the form data

                # Return some json response back to the user
                msg = """ Your data has been modified successfully, thank you! """
                data = dict_alert_msg('True', 'Awesome!', msg, 'success')

            else:
                # Return some json response back to the user
                msg = """ The data has no longer existed, the update has been aborted! """
                data = dict_alert_msg('True', 'Update Failed!', msg, 'error')
        else:

            # Extract form.errors
            msg = None
            msg = [(k, v[0]) for k, v in form_edit.errors.items()]
            data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

        return JsonResponse(data)


def basic_search_text_view(request):
    """Renders the basic search text."""
    if request.method == "POST":
        fsearch = request.POST.get('fsearch')

        # Filter data by using __icontains built-in Django function
        data_lists = ContactUs.objects.filter(
                        Q(is_deleted=False) &
                        (Q(full_name__icontains=fsearch) |
                        Q(email__icontains=fsearch) |
                        Q(subject__icontains=fsearch) |
                        Q(message__icontains=fsearch))).order_by('-id')[:50]

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            url = settings.BASE_URL + slugify(fh.full_name) + "-" + str(fh.id)
            trun_subject = fh.subject[:100] + '...'

            # Convert UTC datetime from db to user's local datetime.
            submitted_date = convert_to_local_datetime(fh.submitted)

            edit_url = settings.BASE_URL + "basic_crud/" + str(fh.id) + "/change/"

            fh_list.append(
                    {'full_name': (fh.full_name),
                     'subject': trun_subject,
                     'email': fh.email,
                     'submitted': submitted_date,
                     'id': fh.id,
                     'url': url,
                     'edit_url': edit_url
                     })

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


def basic_search_dr_view(request):
    """Renders the basic search by date and time."""
    if request.method == "POST":

        # Get the date range values from the user input
        mStartDate = request.POST.get('mStartDate')
        mEndDate = request.POST.get('mEndDate')

        # Format date
        date_format = '%Y-%m-%d'

        unaware_start_date = datetime.strptime(mStartDate, date_format)
        aware_start_date = pytz.utc.localize(unaware_start_date)

        unaware_end_date = datetime.strptime(mEndDate, date_format
                                             ) + timedelta(days=1)
        aware_end_date = pytz.utc.localize(unaware_end_date)

        # Display data, using __range from Django's built-in functionality
        data_lists = ContactUs.objects.filter(
                            is_deleted=False,
                            submitted__range=(aware_start_date,
                                              aware_end_date)
                            ).order_by('-id')[:50]

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            url = settings.BASE_URL + slugify(fh.full_name) + "-" + str(fh.id)
            trun_subject = fh.subject[:100] + '...'

            # Convert UTC datetime from db to user's local datetime.
            submitted_date = convert_to_local_datetime(fh.submitted)

            edit_url = settings.BASE_URL + "basic_crud/" + str(fh.id) + "/change/"

            fh_list.append(
                    {'full_name': (fh.full_name),
                     'subject': trun_subject,
                     'email': fh.email,
                     'submitted': submitted_date,
                     'id': fh.id,
                     'url': url,
                     'edit_url': edit_url
                     })

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


def search_view(request):
    """
    Renders the native Django search with form post submission
    with basic SEO compliance.
    """
    if request.method == "GET":
        fsearch = request.GET.get('q')

        if fsearch and len(fsearch) >= settings.MIN_CHARS_SEARCH:

            # Filter data by using __icontains built-in Django function
            data_lists = ContactUs.objects.filter(
                            Q(is_deleted=False) &
                            (Q(full_name__icontains=fsearch) |
                            Q(email__icontains=fsearch) |
                            Q(subject__icontains=fsearch) |
                            Q(message__icontains=fsearch))).order_by('-id')[:50]

            paginator = Paginator(data_lists, 50)  # Show 50 rows per page
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

            return render(request, 'myroot/search.html',
                          {
                              'title': 'Search Results for: ' + str(fsearch),
                              'meta_desc': 'These are the list of search results based on your search text criteria.',
                              'data_pages': data_pages,
                              'page_range': page_range,
                              'totRows': totRows,
                              'q': fsearch
                           })
        else:
            return redirect('emptysearch')


def emptysearch_view(request):
    """Renders the empty search page."""
    if request.method == 'GET':
        return render(request, 'myroot/empty_search.html',
                      {'title': "Oops! Invalid Search.",
                       'meta_desc': """Either you forget to enter your search text criteria
                       or at least key-in the minimum of 3 characters for the search operation
                       to proceed. Thank You!"""})


def register_view(request):
    """Renders the register page."""
    if request.method == 'GET':

        # Get signup form to display
        form = SignUpForm()
        return render(request, 'myroot/registration/register.html',
                      {'form': form,
                       'title': "Register | " + settings.SITE_SHORT_NAME,
                       'meta_desc': """A step-by-step guide on how to create a user registration form using Django 2.1+ with Python 3.7+""",
                       })

    data = dict()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        is_pass_valid, msg, title = is_password_valid(password1, password2)
        is_user_name_valid, msg1, title1 = is_username_valid(username)

        if not is_user_name_valid:
            # Return some json response back to user
            data = dict_alert_msg('False', title1, msg1, 'error')

        elif not is_pass_valid:
            # Return some json response back to user
            data = dict_alert_msg('False', title, msg, 'error')

        # Check if email exist in our users list
        elif User.objects.filter(email=email):
            # Return some json response back to user
            msg = """A user with that email address already exist."""
            data = dict_alert_msg('False', 'Invalid Email!', msg, 'error')

        elif User.objects.filter(username=username):
            # Return some json response back to user
            msg = """Username already taken, please try another one."""
            data = dict_alert_msg('False', 'Invalid Username!',
                                  msg, 'error')

        # To check prohibited username match with our list
        elif SiteConfig.objects.filter(property_name=username):
            # Return some json response back to user
            msg = """A username you have entered is not allowed."""
            data = dict_alert_msg('False', 'Prohibited Username!',
                                  msg, 'error')

        # To check if Prohibited email match with our list
        elif SiteConfig.objects.filter(property_name=email):
            # Return some json response back to user
            msg = """The email you have entered is not allowed."""
            data = dict_alert_msg('False', 'Prohibited Email!',
                                  msg, 'error')

        else:

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

                    # Proceed with the rest of registering new user
                    user = form.save(commit=False)
                    user.is_active = False
                    user.save()  # Finally save the form data
                    user.pk  # Get the latest id

                    current_site = get_current_site(request)
                    subject = 'Activate Your ' + \
                        str(settings.SITE_SHORT_NAME) + ' Account'
                    message = render_to_string(
                        'myroot/account/account_activation_email.html',
                        {
                            'user': user,
                            'domain': current_site.domain,
                            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                            'token': account_activation_token.make_token(user),
                        })
                    user.email_user(subject, message, settings.APP_EMAIL_FROM)

                    # Return some json response back to user
                    msg = """New user has been created successfully!"""
                    data = dict_alert_msg('True', 'Awesome', msg, 'success')

                else:

                    # Return some json response back to user
                    msg = """Invalid or non-existed email address."""
                    data = dict_alert_msg('False', 'Oops, Invalid Email Address', msg, 'error')

            else:

                # Return some json response back to user
                msg = """Invalid reCAPTCHA, please try again."""
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

    return JsonResponse(data)


def account_activation_sent(request):
    """A page to be displayed after the signup form submitted successfully."""
    return render(request, 'myroot/account/account_activation_sent.html',
                  {'title': 'New ' + str(settings.SITE_SHORT_NAME) +
                   ' Account Activation',
                   'meta_desc': 'New account activation.'})


def activate(request, uidb64, token):
    """ Function to call for new user account activation process."""
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        login(request, user)
        return render(request,
                      'myroot/account/account_activation_complete.html',
                      {
                          'title': 'New Account Activated Successfully',
                          'meta_desc': 'New Account Activated Successfully'
                      }
                      )
    else:
        return render(request,
                      'myroot/account/account_activation_invalid.html',
                      {
                          'title': 'Account Activation Failed',
                          'meta_desc': 'Account Activation Failed'
                      }
                      )


def login_view(request):
    """Renders the login page."""
    if request.user.is_authenticated:
        # User has been Authenticated: redirect to the specified landing page instead
        # and not to display the login page again until the user logout.
        return redirect(settings.APP_USER_AUTH_RE_ACCESS_LOGIN_PAGE)
    else:
        if request.method == 'GET':
            # Get login form to display
            form = LoginAuthenticationForm()
            return render(request, 'myroot/account/login.html',
                          {'form': form, 'title': 'Log in',
                           'meta_desc': settings.SITE_SHORT_NAME + """ Account.
                           Sign in to access your account."""})

    data = dict()
    if request.method == 'POST':
        form = LoginAuthenticationForm(request.POST)
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        chkKeepMe = request.POST.get('chkKeepMe')

        if username and password:

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
                # Check remember me checkbox option
                if chkKeepMe == "true":
                    request.session.set_expiry(2592000)  # 30 days
                else:
                    # session will expire on 12 hrs
                    request.session.set_expiry(43200)

                # Test username/password combination
                user = authenticate(username=username, password=password)
                # Found a match
                if user is not None:

                    # User is active
                    if user.is_active:
                        # Login Successfully Authenticated
                        login(request, user)

                        msg = """User has been successfully login."""
                        data = dict_alert_msg('True', 'Login Successfully',
                                              msg, 'success')

                        data["base_url"] = settings.BASE_URL

                        # Check /next/ url parameter
                        next_url = request.GET.get('next')
                        if next_url:
                            # Strip off "/" at the first string position
                            data["redirect_url"] = next_url[1:]
                        else:
                            data["redirect_url"] = settings.LOGIN_REDIRECT_URL

                    else:

                        # Account is not Active
                        msg = """Sorry, your account is not active, please
                        check your email inbox to verify your account."""
                        data = dict_alert_msg('False', 'Account is not Active',
                                              msg, 'error')
                else:

                    # Invalid username or password
                    msg = """Please enter the correct username and password for your account.
                    Note that both fields may be case-sensitive."""
                    data = dict_alert_msg('False', 'Invalid Login', msg, 'error')

            else:

                # Return some json response back to user
                msg = """Invalid reCAPTCHA, please try again."""
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

            return JsonResponse(data)


def logout_view(request):
    """Renders the logout event."""
    if request.method == 'GET':
        logout(request)

        # Redirect to a success page.
        return redirect('/login/')


def password_reset_view(request):
    """Renders the password reset page."""
    if request.method == 'GET':
        # Get password reset form to display
        form = PasswordResetForm()
        return render(request, 'myroot/account/password_reset_form.html',
                      {'form': form, 'title': 'Reset Password',
                       'meta_desc': """We can help you to reset your password using your
                       registered email linked to your account."""})

    data = dict()
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)

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
                # Check first if email existed in our users data
                if User.objects.filter(email=form.cleaned_data.get("email")):
                    # Setup email template
                    opts = {
                        'use_https': request.is_secure(),
                        'token_generator': default_token_generator,
                        'from_email': settings.APP_EMAIL_FROM,
                        'email_template_name': 'myroot/account/password_reset_email.html',
                        'subject_template_name': 'myroot/account/password_reset_subject.txt',
                        'request': request
                    }
                    form.save(**opts)

                    msg = """Password reset request sent successfully."""
                    data = dict_alert_msg('True', 'Password Reset Sent!',
                                          msg, 'success')
                    data["redirect_url"] = 'password_reset_done'
                    data["base_url"] = settings.BASE_URL

                else:

                    # Email submitted is not found in our users data
                    msg = """Email is not registered, please try again."""
                    data = dict_alert_msg('False', 'Email is Not Registered!',
                                          msg, 'warning')
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


def password_reset_done_view(request):
    """Renders the password reset done page."""
    if request.method == 'GET':
        # Get password reset done page to display
        return render(request, 'myroot/account/password_reset_done.html',
                      {'title': 'Password Reset Sent',
                       'meta_desc': """We've emailed you instructions for setting your password, if an account exists with the email you entered. You should receive them shortly.
                       If you don't receive an email, please make sure you've entered the address you registered with, and check your spam folder."""})


def password_reset_confirm_view(request, uidb64, token):
    """Renders my own password change page."""
    if request.method == 'GET':
        # Get user info
        current_user = request.user
        formChangePassword = PasswordResetConfirmForm(current_user.username)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            validlink = True
        else:
            validlink = False

        return render(request, 'myroot/account/password_reset_confirm.html',
                      {
                          'title': 'Password Reset Confirm',
                          'meta_desc': 'Password Reset Confirm.',
                          'formChangePassword': formChangePassword,
                          'validlink': validlink,
                          'username': user
                       })


def reset_password_now_view(request):
    """Custom Password Reset triggered from the AJAX post."""
    data = dict()
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')
        username = request.POST.get('username')

        is_pass_valid, msg, title = is_password_valid(new_password1, new_password2)

        if not is_pass_valid:
            # Return some json response back to user
            data = dict_alert_msg('False', title, msg, 'error')

        else:

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
                # Check first if email existed in our users data
                if User.objects.filter(username=username):

                    # Change the password now
                    u = User.objects.get(username=username)
                    u.set_password(new_password1)
                    u.save()

                    msg = """Your new password was successfully changed."""
                    data = dict_alert_msg('True', 'Password Changed',
                                          msg, 'success')
                else:

                    # The username submitted is not found in our users data
                    msg = """Oops, username not found, please try again."""
                    data = dict_alert_msg('False', 'Username Not Found!',
                                          msg, 'error')
            else:

                # Return some json response back to user
                msg = """Invalid reCAPTCHA, please try again."""
                data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

        return JsonResponse(data)


def password_reset_complete_view(request):
    """Renders the password reset complete page."""
    if request.method == 'GET':
        # Get password reset done page to display
        return render(request, 'myroot/account/password_reset_complete.html',
                      {'title': 'Password Reset Complete',
                       'meta_desc': """Your password has been set, you can login with your account with us now."""})


def contactus_with_celery_view(request):
    """Renders the contact us page with Celery task when sending an email."""
    if request.method == 'GET':

        # Get contact us form to display
        form = Basic_CRUD_Create_Form()
        return render(request, 'myroot/contactus_with_celery.html',
                      {'form': form, 'title': "Learn Django Celery with Real-time Monitoring Tasks Using Flower",
                       'meta_desc': """Learn how to separate the time-consuming process and sent it to the Celery
                       to process it separately so that the rest of the sequence will keep continuing processing the
                       rest of the codes without delay. - """ + settings.SITE_FULL_NAME})

    data = dict()
    if request.method == 'POST':
        form = Basic_CRUD_Create_Form(request.POST)
        GET_USER_TZN = request.POST.get('GET_USER_TZN')

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
                # Save form data successfully
                form.save()

                # Return some json response back to user
                msg = """ Your inquiry was sent successfully, thank you! """
                data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                subject = form.cleaned_data.get("subject")
                email = form.cleaned_data.get("email")
                full_name = form.cleaned_data.get("full_name")
                message = form.cleaned_data.get("message")

                # Call the celery task async
                contactus_send_mail.delay(subject, email, full_name, message, GET_USER_TZN)

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


def contactus_without_celery_view(request):
    """Renders the contact us page without Celery task when sending an email."""
    if request.method == 'GET':

        # Get contact us form to display
        form = Basic_CRUD_Create_Form()
        return render(request, 'myroot/contactus_without_celery.html',
                      {'form': form, 'title': "See the Difference Without the Django Celery Distributed Tasks.",
                       'meta_desc': """To illustrate the difference between the normal sending email without the Django Celery to
                       separate the time-consuming process and sent it to the Celery
                       to process it separately so that the rest of the sequence will keep continuing processing the
                       rest of the codes without delay. - """ + settings.SITE_FULL_NAME})

    data = dict()
    if request.method == 'POST':
        form = Basic_CRUD_Create_Form(request.POST)
        GET_USER_TZN = request.POST.get('GET_USER_TZN')

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
                # Save form data successfully
                form.save()

                # Return some json response back to user
                msg = """ Your inquiry was sent successfully, thank you! """
                data = dict_alert_msg('True', 'Awesome!', msg, 'success')

                subject = form.cleaned_data.get("subject")
                email = form.cleaned_data.get("email")
                full_name = form.cleaned_data.get("full_name")
                message = form.cleaned_data.get("message")

                # Send an email without the Celery triggered event
                do_send_email('email_contactus_with_celery.html',
                              subject,
                              settings.APP_EMAIL_FROM,
                              (email,),
                              'Thank you for getting in touch!',
                              arrow.utcnow().to(GET_USER_TZN).format('MMM DD, YYYY hh:mm a'),
                              'Awesome!',
                              full_name,
                              None,
                              message)

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


def cache_basic_crud_list_view(request):
    """
    This is how we cache an expensive Django queries to avoid
    keep hitting your database server with the same results.
    """
    if request.method == "GET":

        # Call a cachable function.
        db_data = get_contact_us_list()

        return render(request, 'myroot/cache_basic_crud_list.html',
                      {
                          'title': 'Django Memcached Basic CRUD: Manage Table Rows using DataTables',
                          'meta_desc': 'Learn how to use the Django Memcached to display the database table rows using DataTables.',
                          'db_data': db_data
                       })


def cache_basic_crud_update_row_view(request, id):
    """
    Renders the Django edit form page and execute the update statement.
    But, with invalidating the cache to clear the previous cached results.
    """
    if request.method == "GET":

        # Check if the row id existed or not.
        if is_contact_us_id_exist(id):

            # Edit the form data.
            edit_data = ContactUs.objects.get(id=id, is_deleted=False)
            formEdit = Basic_CRUD_Create_Form(instance=edit_data)

            return render(request, 'myroot/cache_basic_crud_update.html',
                          {
                              'title': "Django Memcached Basic CRUD Update Statement",
                              'meta_desc': "This is the actual example for Django Memcached using the django-cache-memoize invalidation, basic crud which is the update statement.",
                              'id': id,
                              'formEdit': formEdit
                           })
        else:
            raise Http404()

    data = dict()
    if request.method == "POST":

        # Get the  form modified data
        form_edit = Basic_CRUD_Create_Form(request.POST)
        id = request.POST.get('id')

        if form_edit.is_valid():

            # Check if the row still not deleted, get it from the cache memory
            if is_contact_us_id_exist(id):

                # Get the form edit instance
                update_data = ContactUs.objects.get(id=id, is_deleted=False)

                # Now, supply the form data to an instance
                form_edit = Basic_CRUD_Create_Form(request.POST, instance=update_data)
                form_edit.save()  # Finally save the form data

                # Here, to invalidate the previous cache results.
                get_contact_us_list.invalidate()
                is_contact_us_id_exist.invalidate(id)

                # Return some json response back to the user
                msg = """ Your data has been modified successfully, thank you! """
                data = dict_alert_msg('True', 'Awesome!', msg, 'success')

            else:
                # Return some json response back to the user
                msg = """ The data has no longer existed, the update has been aborted! """
                data = dict_alert_msg('True', 'Update Failed!', msg, 'error')
        else:

            # Extract form.errors
            msg = None
            msg = [(k, v[0]) for k, v in form_edit.errors.items()]
            data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

        return JsonResponse(data)
