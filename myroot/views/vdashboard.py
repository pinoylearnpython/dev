from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

# Django Auth System
from django.contrib.auth.models import User
import requests

# Call myroot properties
from myroot.forms.fmain import ChangePasswordForm
from myroot.views.vfunctions import (dict_alert_msg, is_password_valid)


@login_required
def dashboard_view(request):
    """Renders the dashboard page."""
    if request.method == "GET":

        # Set session for the main left side bar active menu
        request.session['active_sidebar_menu'] = "dashboard"

        return render(request, 'myroot/dashboard/index.html',
                      {
                          'title': 'Dashboard',
                          'meta_desc': 'Welcome to your dashboard',
                          'active_sidebar_menu': request.session['active_sidebar_menu']
                       })


@login_required
def change_password_view(request):
    """Renders the custom change password from the user's dashboard page."""
    if request.method == "GET":

        # Get user info
        current_user = request.user
        formChangePassword = ChangePasswordForm(current_user.username)

        # Set session for the main left side bar active menu
        request.session['active_sidebar_menu'] = "change_password"

        return render(request, 'myroot/account/change_password.html',
                      {
                          'title': 'Change Password',
                          'meta_desc': 'Change your password.',
                          'formChangePassword': formChangePassword,
                          'active_sidebar_menu': request.session['active_sidebar_menu']
                       })

    data = dict()
    if request.method == 'POST':
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # Get user info
        current_user = request.user

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
                if User.objects.filter(username=current_user.username):

                    # Change the password now
                    u = User.objects.get(username=current_user.username)
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
