from django.conf import settings


def global_settings(request):
    """ Return custom constant global variables to be
    used widely for all of our apps. """

    # Current user logged in info
    cur_user_id = 0
    cur_user_name = ''
    cur_user_full_name = ''

    if request.user.is_authenticated:
        # Get user info
        cur_user_id = request.user.id
        cur_user_name = request.user.username
        cur_user_full_name = request.user.first_name + " " + request.user.last_name

    return{
        'BASE_URL': settings.BASE_URL,
        'SITE_SHORT_NAME': settings.SITE_SHORT_NAME,
        'SITE_FULL_NAME': settings.SITE_FULL_NAME,
        'SITE_YEAR_STARTED': settings.SITE_YEAR_STARTED,
        'SITE_URL_HOME': settings.SITE_URL_HOME,
        'SITE_SLOGAN': settings.SITE_SLOGAN,
        'SITE_CONTACT_US': settings.SITE_CONTACT_US,
        'MIN_CHARS_SEARCH': settings.MIN_CHARS_SEARCH,
        'APP_URL_TOP_LOGO': settings.APP_URL_TOP_LOGO,
        'GRECAP_SITE_KEY': settings.GRECAP_SITE_KEY,
        'DEFAULT_AVATAR': settings.DEFAULT_AVATAR,
        'CUR_USER_ID': cur_user_id,
        'CUR_USER_name': cur_user_name,
        'CUR_USER_full_name': cur_user_full_name.strip(),
    }
