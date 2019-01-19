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
