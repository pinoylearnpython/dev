from django.conf import settings
from django.db import models


class ContactUs(models.Model):
    full_name = models.CharField(max_length=75)
    email = models.EmailField(max_length=254)
    subject = models.CharField(max_length=75)
    message = models.TextField()
    submitted = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)
    deleted_date = models.DateField(null=True, blank=True)
    deleted_by = models.PositiveIntegerField(default=0)

    class Meta:
        index_together = ["full_name", "is_deleted"]
        db_table = 'dev_contact_us'
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us'


class SiteConfig(models.Model):
    property_name = models.CharField(max_length=75, unique=True)
    property_value = models.CharField(max_length=254, null=True, blank=True)
    property_desc = models.CharField(max_length=255, null=True, blank=True)

    SC_Default = 'APPSETTING'
    SC_Option = (
        ('APP_CONF', 'App Setting'),
        ('GENERAL_CONF', 'General Setting'),
        ('PROHIBITED_USER_NAME', 'Prohibited User Name'),
        ('PROHIBITED_USER_EMAIL', 'Prohibited User Email'),
        ('OTHERS', 'Other'),
    )

    property_group = models.CharField(max_length=75, choices=SC_Option,
                                      default=SC_Default)

    class Meta:
        index_together = ["property_group"]
        db_table = 'dev_site_config'
        verbose_name = 'Site Config'
        verbose_name_plural = 'Site Configs'
