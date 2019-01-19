from django.conf import settings


def global_settings(request):
    """ Return custom constant global variables to be
    used widely for all of our apps. """
    return{
        'BASE_URL': settings.BASE_URL,
        'SITE_SHORT_NAME': settings.SITE_SHORT_NAME,
        'SITE_FULL_NAME': settings.SITE_FULL_NAME,
        'SITE_YEAR_STARTED': settings.SITE_YEAR_STARTED,
        'SITE_URL_HOME': settings.SITE_URL_HOME,
        'SITE_SLOGAN': settings.SITE_SLOGAN,
        'SITE_CONTACT_US': settings.SITE_CONTACT_US,
        'MIN_CHARS_SEARCH': settings.MIN_CHARS_SEARCH,
    }
