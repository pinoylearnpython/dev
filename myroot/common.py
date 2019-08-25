from django.conf import settings
from cache_memoize import cache_memoize

# Call all myroot app properties
from myroot.models import ContactUs


@cache_memoize(3600)
def get_contact_us_list():
    """
    Function to get the contact us list, cache this function
    for 3600 seconds equivalent to 1 hr, to relieve the stress
    of the database server.
    """
    # fetch the latest 50 rows as an example.
    data = ContactUs.objects.filter(is_deleted=False).order_by('-id')[:50]
    return data


@cache_memoize(3600)
def is_contact_us_id_exist(contact_us_id):
    """
    Function to check if the contact us id existed or not.
    Cache this for 3600 seconds equivalent to 1 hr, to relieve the stress
    of the database server.
    """
    # fetch the latest 50 rows as an example.
    if ContactUs.objects.filter(id=contact_us_id, is_deleted=False).exists():
        return True
    else:
        return False
