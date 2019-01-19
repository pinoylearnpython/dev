from django.contrib import admin

# Call myroot properties
from myroot.models import ContactUs


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
