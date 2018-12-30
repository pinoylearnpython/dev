from django.apps import AppConfig
from django.conf import settings


class myrootConfig(AppConfig):
    """ Class to call our 'myroot' app structural name """
    name = settings.APP_LABEL_MYROOT
