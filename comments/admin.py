from django.conf import settings
from import_export.admin import ImportExportModelAdmin
from django.contrib import admin

from bp.models import (Business, BusinessTag, BusinessComment, BusinessReview,
                       BusinessInquiry)
from bp.resources import (BusinessResource, BusinessTagResource,
                          BusinessCommentResource, BusinessReviewResource,
                          BusinessInquiryResource)


class BusinessAdmin(ImportExportModelAdmin):
    using = settings.APP_LABEL_BP

    list_display = ('id', 'company_name', 'tel_no', 'fax_no', 'email',
                    'is_active', 'is_deleted', 'created_by', 'created_date')
    search_fields = ['id', 'company_name', 'address', 'tel_no', 'fax_no',
                     'email', 'website', 'office_hours', 'short_desc', 'about',
                     'created_by']
    fieldsets = (
        (None, {
            'fields': ('company_name', 'address', 'tel_no', 'fax_no', 'email',
                       'website', 'is_website_no_follow', 'office_hours',
                       'short_desc', 'about', 'is_active', 'created_by',
                       'modified_by', 'modified_date', 'is_deleted',
                       'deleted_by', 'deleted_date')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    resource_class = BusinessResource


admin.site.register(Business, BusinessAdmin)


class BusinessTagAdmin(ImportExportModelAdmin):
    using = settings.APP_LABEL_BP

    list_display = ('id', 'business_id', 'tag_name', 'tag_name_slug',
                    'is_active', 'is_deleted', 'created_by', 'created_date')
    search_fields = ['id', 'business_id', 'tag_name', 'tag_name_slug',
                     'is_active', 'created_by']
    fieldsets = (
        (None, {
            'fields': ('business_id', 'tag_name', 'tag_name_slug', 'is_active',
                       'created_by', 'modified_by', 'modified_date',
                       'is_deleted', 'deleted_by', 'deleted_date')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    resource_class = BusinessTagResource


admin.site.register(BusinessTag, BusinessTagAdmin)


class BusinessCommentAdmin(ImportExportModelAdmin):
    using = settings.APP_LABEL_BP

    list_display = ('id', 'business_id', 'full_name', 'is_active',
                    'is_deleted', 'created_by', 'created_date')
    search_fields = ['id', 'business_id', 'full_name', 'comment', 'created_by']
    fieldsets = (
        (None, {
            'fields': ('business_id', 'full_name', 'comment', 'is_active',
                       'created_by', 'modified_by', 'modified_date',
                       'is_deleted', 'deleted_by', 'deleted_date')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    resource_class = BusinessCommentResource


admin.site.register(BusinessComment, BusinessCommentAdmin)


class BusinessReviewAdmin(ImportExportModelAdmin):
    using = settings.APP_LABEL_BP

    list_display = ('id', 'business_id', 'full_name', 'email', 'rate',
                    'is_active', 'is_deleted', 'created_by',
                    'created_date')
    search_fields = ['id', 'business_id', 'full_name', 'email', 'rate',
                     'review', 'created_by']
    fieldsets = (
        (None, {
            'fields': ('business_id', 'full_name', 'email', 'rate', 'review',
                       'is_active', 'created_by', 'modified_by',
                       'modified_date', 'is_deleted', 'deleted_by',
                       'deleted_date')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    resource_class = BusinessReviewResource


admin.site.register(BusinessReview, BusinessReviewAdmin)


class BusinessInquiryAdmin(ImportExportModelAdmin):
    using = settings.APP_LABEL_BP

    list_display = ('id', 'business_id', 'full_name', 'email', 'subject',
                    'is_active', 'is_deleted', 'created_by',
                    'created_date')
    search_fields = ['id', 'business_id', 'full_name', 'email', 'subject',
                     'inquiry', 'created_by']
    fieldsets = (
        (None, {
            'fields': ('business_id', 'full_name', 'email', 'subject',
                       'inquiry', 'is_active', 'created_by', 'modified_by',
                       'modified_date', 'is_deleted', 'deleted_by',
                       'deleted_date')
        }),
    )

    def save_model(self, request, obj, form, change):
        # Tell Django to save objects to the 'other' database.
        obj.save(using=self.using)

    def delete_model(self, request, obj):
        # Tell Django to delete objects from the 'other' database
        obj.delete(using=self.using)

    def get_queryset(self, request):
        # Tell Django to look for objects on the 'other' database.
        return super().get_queryset(request).using(self.using)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Tell Django to populate ForeignKey widgets using a query
        # on the 'other' database.
        return super().formfield_for_foreignkey(db_field, request, using=self.using, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Tell Django to populate ManyToMany widgets using a query
        # on the 'other' database.
        return super().formfield_for_manytomany(db_field, request, using=self.using, **kwargs)

    resource_class = BusinessInquiryResource


admin.site.register(BusinessInquiry, BusinessInquiryAdmin)
