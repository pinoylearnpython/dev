from django.conf import settings
from django.db import models


class Business(models.Model):
    company_name = models.CharField(max_length=125)
    address = models.CharField(max_length=255)
    tel_no = models.CharField(max_length=75)
    fax_no = models.CharField(max_length=75, null=True, blank=True)
    email = models.CharField(max_length=254)
    website = models.CharField(max_length=255, null=True, blank=True)
    is_website_no_follow = models.BooleanField(default=False)
    office_hours = models.CharField(max_length=75, null=True, blank=True)
    short_desc = models.CharField(max_length=455)
    about = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.PositiveIntegerField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.PositiveIntegerField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        index_together = ["company_name", "address", "tel_no",
                          "fax_no", "short_desc", "is_active",
                          "is_deleted"]
        app_label = str(settings.APP_LABEL_BP)
        db_table = 'bp_business'
        verbose_name = 'Business'
        verbose_name_plural = 'Businesses'


class BusinessTag(models.Model):
    business_id = models.PositiveIntegerField(default=0)
    tag_name = models.CharField(max_length=100)
    tag_name_slug = models.CharField(max_length=255)
    is_active = models.BooleanField(default=False)
    created_by = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.PositiveIntegerField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.PositiveIntegerField(null=True, blank=True)
    deleted_date = models.DateField(null=True, blank=True)

    class Meta:
        index_together = ["business_id", "is_active", "created_by",
                          "is_deleted"]
        app_label = str(settings.APP_LABEL_BP)
        db_table = 'bp_business_tag'
        verbose_name = 'Business Tag'
        verbose_name_plural = 'Business Tags'


class BusinessComment(models.Model):
    business_id = models.PositiveIntegerField()
    full_name = models.CharField(max_length=75)
    comment = models.TextField()
    is_active = models.BooleanField(default=False)
    created_by = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.PositiveIntegerField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.PositiveIntegerField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        index_together = ["business_id", "is_active", "created_by",
                          "is_deleted"]
        app_label = str(settings.APP_LABEL_BP)
        db_table = 'bp_business_comment'
        verbose_name = 'Business Comment'
        verbose_name_plural = 'Business Comments'


class BusinessReview(models.Model):
    business_id = models.PositiveIntegerField()
    full_name = models.CharField(max_length=75)
    email = models.CharField(max_length=80)
    rate = models.PositiveSmallIntegerField()
    review = models.TextField()
    is_active = models.BooleanField(default=False)
    created_by = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.PositiveIntegerField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.PositiveIntegerField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        index_together = ["business_id", "is_active", "created_by",
                          "is_deleted"]
        app_label = str(settings.APP_LABEL_BP)
        db_table = 'bp_business_review'
        verbose_name = 'Business Review'
        verbose_name_plural = 'Business Reviews'


class BusinessInquiry(models.Model):
    business_id = models.PositiveIntegerField()
    full_name = models.CharField(max_length=75)
    email = models.CharField(max_length=80)
    subject = models.CharField(max_length=75)
    inquiry = models.TextField()
    is_active = models.BooleanField(default=False)
    created_by = models.PositiveIntegerField(default=0)
    created_date = models.DateTimeField(auto_now_add=True)
    modified_by = models.PositiveIntegerField(null=True, blank=True)
    modified_date = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    deleted_by = models.PositiveIntegerField(null=True, blank=True)
    deleted_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        index_together = ["business_id", "is_active", "is_deleted"]
        app_label = str(settings.APP_LABEL_BP)
        db_table = 'bp_business_inquiry'
        verbose_name = 'Business Inquiry'
        verbose_name_plural = 'Business Inquiries'


class BusinessNotifications(models.Model):
    user_id = models.PositiveIntegerField(default=0)
    event_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    business_id = models.PositiveIntegerField(default=0)
    src_id = models.PositiveIntegerField(default=0)
    src_type = models.CharField(max_length=2,
                                choices=settings.NOTIFY_BP_TYPE_LISTS)

    class Meta:
        index_together = ["user_id", "src_id", "business_id", "event_date"]
        app_label = settings.APP_LABEL_BP
        db_table = 'bp_business_notification'
        verbose_name = 'Business Notification'
        verbose_name_plural = 'Business Notifications'


class BusinessNotificationsRead(models.Model):
    notify_id = models.PositiveIntegerField(default=0)
    user_id = models.PositiveIntegerField(default=0)
    read_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    class Meta:
        index_together = ["notify_id", "user_id"]
        app_label = settings.APP_LABEL_BP
        db_table = 'bp_business_notification_read'
        verbose_name = 'Business Notification Read'
        verbose_name_plural = 'Business Notification Reads'
