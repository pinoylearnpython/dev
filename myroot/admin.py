from django.contrib import admin

# Call myroot properties
from myroot.models import ContactUs, SiteConfig


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'email',
                    'subject', 'submitted')
    search_fields = ['id', 'full_name', 'email', 'subject', 'message']
    fieldsets = (
        (None, {
            'fields': ('full_name', 'email',
                       'subject', 'message', 'is_deleted',
                       'deleted_date', 'deleted_by')
        }),
    )


admin.site.register(ContactUs, ContactUsAdmin)


class SiteConfigAdmin(admin.ModelAdmin):
    list_display = ('id', 'property_name', 'property_value', 'property_desc',
                    'property_group')
    search_fields = ['id', 'property_name', 'property_value', 'property_desc',
                     'property_group']
    list_filter = ('property_group', )
    fieldsets = (
        (None, {
            'fields': ('property_name', 'property_value', 'property_desc',
                       'property_group')
        }),
    )


admin.site.register(SiteConfig, SiteConfigAdmin)
