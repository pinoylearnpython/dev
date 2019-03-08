from django.conf import settings
from django.contrib import sitemaps
from django.urls import reverse
from django.utils.text import slugify

# Call myroot properties
from myroot.models import ContactUs


class ContactUsSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'
    protocol = "https"

    def items(self):
        contacts = ContactUs.objects.filter(is_deleted=False).order_by('-id')[:250]  # latest 250 new entries
        return contacts

    def lastmod(self, item):
        mod_date = item.submitted  # Actual datetime field
        return mod_date

    def location(self, item):
        url = '/' + slugify(item.full_name) + '-' + str(item.id)  # Actual URL of the individual page
        return url


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = 'daily'
    protocol = "https"

    def items(self):
        return ['helloworld', 'basic_crud_create', 'basic_crud_list', 'register', 'password_reset', 'login']

    def location(self, item):
        return reverse(item)
