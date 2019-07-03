from datetime import datetime, timedelta
import timeago
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.conf import settings
import re


def dict_alert_msg(form_is_valid, alert_title, alert_msg, alert_type):
    """
    Function to call internal alert message to the user with the required
    paramaters: form_is_valid[True/False all small letters for json format],
    alert_title='string', alert_msg='string',
    alert_type='success, error, warning, info'
    """
    data = {
        'form_is_valid': form_is_valid,
        'alert_title': alert_title,
        'alert_msg': alert_msg,
        'alert_type': alert_type
    }
    return data


def convert_to_local_datetime(dt_value):
    MY_DT_FORMAT = '%Y-%m-%d %H:%M:%S'
    dt = dt_value
    created_date_str = dt.strftime(MY_DT_FORMAT)  # convert to string
    created_date = dt.strptime(created_date_str, MY_DT_FORMAT)

    # timeago in python library to get user's local time
    now = datetime.now() + timedelta(seconds=60 * 3.4)
    event_date = timeago.format(created_date, now)

    return str(event_date)


def is_email_valid(email):
    try:
        validate_email(email)
    except ValidationError:
        return False
    return True


def is_password_valid(new_password1, new_password2):
    """
    To check if password is valid or not.
    """
    is_pass_valid = False
    msg, title = '', ''

    if new_password1 != new_password2:
        # Display error message
        msg = "Passwords do not match, please try again."
        title = 'Password Not Match'

    elif len(new_password1) < settings.MIN_PASS_LENGTH:
        # Display error message
        msg = "This password must contain at least " + str(settings.MIN_PASS_LENGTH) + " characters."
        title = 'Password Too Short'

    elif not re.findall('\d', new_password1):
        # Display error message
        msg = "The password must contain at least 1 digit from 0-9."
        title = 'Password No Number'

    elif not re.findall('[A-Z]', new_password1):
        # Display error message
        msg = "The password must contain at least 1 uppercase letter from A-Z."
        title = 'Password No Upper'

    elif not re.findall('[a-z]', new_password1):
        # Display error message
        msg = "The password must contain at least 1 lowercase letter from a-z."
        title = 'Password No Lower'

    else:
        is_pass_valid = True

    return is_pass_valid, msg, title


def is_username_valid(username):
    """
    To check if the username is valid or not.
    """
    is_user_name_valid = False
    msg, title = '', ''

    if not re.findall(r'^[\w.@+-]+\Z', username):
        # Display error message, only allow special characters @, ., +, -, and _.
        msg = "Enter a valid username. This value may contain only alphanumeric values and @/./+/-/_ characters."
        title = 'Invalid Username'
    else:
        is_user_name_valid = True

    return is_user_name_valid, msg, title
