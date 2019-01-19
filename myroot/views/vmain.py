from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.http import Http404
from django.utils.text import slugify
from django.db.models import Q
import json
import pytz
from datetime import datetime, timedelta
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect

# Call myroot properties
from myroot.forms.fmain import Basic_CRUD_Create_Form
from myroot.views.vfunctions import dict_alert_msg, convert_to_local_datetime
from myroot.models import ContactUs


def hello_world_view(request):
    """Renders the Hello World page."""
    if request.method == 'GET':
        return render(request, 'myroot/hello_world.html',
                      {'title': 'Hello World!',
                       'meta_desc': "The complete step-by-step guide in displaying Hello World using Django Template with NGINX guide to set up a new website from scratch.",
                       'BASE_URL': settings.BASE_URL,
                       'mtest': settings.STATIC_ROOT})


def basic_crud_create_view(request):
    """Renders the basic crud create operation."""
    if request.method == 'GET':

        # Get contact us form to display
        form = Basic_CRUD_Create_Form()
        return render(request, 'myroot/basic_crud_create.html',
                      {'form': form,
                       'title': "Django Basic CRUD: CREATE New Row with Actual Example",
                       'meta_desc': """Learn Django basic CRUD to create a new rows and store it on dev_contact_us database table - """ + settings.SITE_FULL_NAME})

    data = dict()
    if request.method == 'POST':
        # Get the form data
        form = Basic_CRUD_Create_Form(request.POST)

        if form.is_valid():
            form.save()  # insert new row

            # Return some json response back to the user
            msg = """ Your data has been inserted successfully, thank you! """
            data = dict_alert_msg('True', 'Awesome!', msg, 'success')

        else:

            # Extract form.errors
            msg = None
            msg = [(k, v[0]) for k, v in form.errors.items()]
            data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

        return JsonResponse(data)


def basic_crud_list_view(request):
    """
    This is the main Django Template to display the recent Basic CRUD
    table rows that you can manage using DataTable object.
    """
    if request.method == "GET":

        db_data = ContactUs.objects.filter(
                is_deleted=False
                ).order_by('-id')[:50] # fetch the latest 50 rows

        return render(request, 'myroot/basic_crud_list.html',
                      {
                          'title': 'Django Basic CRUD: Manage Table Rows using DataTables',
                          'meta_desc': 'Learn how to display the database table rows using DataTables.',
                          'db_data': db_data
                       })


def basic_crud_del_row_view(request):
    """To delete selected row data"""
    data = dict()
    if request.method == 'POST':
        row_id = request.POST.get('row_id')

        # Just update 'is_deleted=False' status of the row only
        ContactUs.objects.filter(
                id=row_id).update(is_deleted=True,
                                  deleted_by=1,
                                  deleted_date=timezone.now())

        # Return some json response back to the user
        msg = """Poof! Your selected data row has been deleted!"""
        data = dict_alert_msg('True', 'Success!', msg, 'success')
        return JsonResponse(data)


def basic_crud_dynamic_public_page_view(request, slug, id):
    """Renders the dynamic public page."""
    if request.method == 'GET':

        # Get match table row by id
        db_data = ContactUs.objects.filter(is_deleted=False, id=id)

        # Use for loop to get the filtered row from a database table
        meta_title = ""
        meta_desc = ""

        for d in db_data:
            meta_title = d.full_name
            meta_desc = d.subject

        if db_data.count():
            return render(request, 'myroot/basic_django_dynamic_public_page.html',
                          {'title': meta_title + " - Django Basic Dynamic Public Page" + ' [' + str(id) + ']',
                           'meta_desc': meta_desc + ' [' + str(id) + ']',
                           'db_data': db_data})
        else:
            raise Http404()


def basic_crud_update_row_view(request, id):
    """Renders the Django edit form page and execute the update statement."""
    if request.method == "GET":

        # Get the selected row information
        db_data = ContactUs.objects.filter(id=id, is_deleted=False)

        if db_data:

            # Edit form data
            edit_data = ContactUs.objects.get(id=id, is_deleted=False)
            formEdit = Basic_CRUD_Create_Form(instance=edit_data)

            return render(request, 'myroot/basic_crud_update.html',
                          {
                              'title': 'Django Basic CRUD Update Statement',
                              'meta_desc': 'This is the actual example on Django basic crud which is the update statement.',
                              'id': id,
                              'formEdit': formEdit
                           })
        else:
            raise Http404()

    data = dict()
    if request.method == "POST":

        # Get the  form modified data
        form_edit = Basic_CRUD_Create_Form(request.POST)
        id = request.POST.get('id')

        if form_edit.is_valid():

            # Check if the row still not deleted
            if ContactUs.objects.filter(id=id, is_deleted=False).exists():

                # Get the form edit instance
                update_data = ContactUs.objects.get(id=id, is_deleted=False)

                # Now, supply the form data to an instance
                form_edit = Basic_CRUD_Create_Form(request.POST, instance=update_data)
                form_edit.save()  # Finally save the form data

                # Return some json response back to the user
                msg = """ Your data has been modified successfully, thank you! """
                data = dict_alert_msg('True', 'Awesome!', msg, 'success')

            else:
                # Return some json response back to the user
                msg = """ The data has no longer existed, the update has been aborted! """
                data = dict_alert_msg('True', 'Update Failed!', msg, 'error')
        else:

            # Extract form.errors
            msg = None
            msg = [(k, v[0]) for k, v in form_edit.errors.items()]
            data = dict_alert_msg('False', 'Oops, Error', msg, 'error')

        return JsonResponse(data)


def basic_search_text_view(request):
    """Renders the basic search text."""
    if request.method == "POST":
        fsearch = request.POST.get('fsearch')

        # Filter data by using __icontains built-in Django function
        data_lists = ContactUs.objects.filter(
                        Q(is_deleted=False) &
                        (Q(full_name__icontains=fsearch) |
                        Q(email__icontains=fsearch) |
                        Q(subject__icontains=fsearch) |
                        Q(message__icontains=fsearch))).order_by('-id')[:50]

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            url = settings.BASE_URL + slugify(fh.full_name) + "-" + str(fh.id)
            trun_subject = fh.subject[:100] + '...'

            # Convert UTC datetime from db to user's local datetime.
            submitted_date = convert_to_local_datetime(fh.submitted)

            edit_url = settings.BASE_URL + "basic_crud/" + str(fh.id) + "/change/"

            fh_list.append(
                    {'full_name': (fh.full_name),
                     'subject': trun_subject,
                     'email': fh.email,
                     'submitted': submitted_date,
                     'id': fh.id,
                     'url': url,
                     'edit_url': edit_url
                     })

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


def basic_search_dr_view(request):
    """Renders the basic search by date and time."""
    if request.method == "POST":

        # Get the date range values from the user input
        mStartDate = request.POST.get('mStartDate')
        mEndDate = request.POST.get('mEndDate')

        # Format date
        date_format = '%Y-%m-%d'

        unaware_start_date = datetime.strptime(mStartDate, date_format)
        aware_start_date = pytz.utc.localize(unaware_start_date)

        unaware_end_date = datetime.strptime(mEndDate, date_format
                                             ) + timedelta(days=1)
        aware_end_date = pytz.utc.localize(unaware_end_date)

        # Display data, using __range from Django's built-in functionality
        data_lists = ContactUs.objects.filter(
                            is_deleted=False,
                            submitted__range=(aware_start_date,
                                                 aware_end_date)
                            ).order_by('-id')[:50]

        fh_data = dict()
        fh_list = []

        for fh in data_lists:
            url = settings.BASE_URL + slugify(fh.full_name) + "-" + str(fh.id)
            trun_subject = fh.subject[:100] + '...'

            # Convert UTC datetime from db to user's local datetime.
            submitted_date = convert_to_local_datetime(fh.submitted)

            edit_url = settings.BASE_URL + "basic_crud/" + str(fh.id) + "/change/"

            fh_list.append(
                    {'full_name': (fh.full_name),
                     'subject': trun_subject,
                     'email': fh.email,
                     'submitted': submitted_date,
                     'id': fh.id,
                     'url': url,
                     'edit_url': edit_url
                     })

        fh_data = fh_list
        json_data = json.dumps(fh_data)
        return JsonResponse(json_data, safe=False)


def search_view(request):
    """
    Renders the native Django search with form post submission
    with basic SEO compliance.
    """
    if request.method == "GET":
        fsearch = request.GET.get('q')

        if fsearch and len(fsearch) >= settings.MIN_CHARS_SEARCH:

            # Filter data by using __icontains built-in Django function
            data_lists = ContactUs.objects.filter(
                            Q(is_deleted=False) &
                            (Q(full_name__icontains=fsearch) |
                            Q(email__icontains=fsearch) |
                            Q(subject__icontains=fsearch) |
                            Q(message__icontains=fsearch))).order_by('-id')[:50]

            paginator = Paginator(data_lists, 50)  # Show 50 rows per page
            page = request.GET.get('page', 1)

            try:
                data_pages = paginator.page(page)
            except PageNotAnInteger:
                data_pages = paginator.page(1)
            except EmptyPage:
                data_pages = paginator.page(paginator.num_pages)

            # Get the index of the current page
            index = data_pages.number - 1  # edited to something easier without index
            max_index = len(paginator.page_range)
            start_index = index - 5 if index >= 5 else 0
            end_index = index + 5 if index <= max_index - 5 else max_index
            page_range = list(paginator.page_range)[start_index:end_index]
            totRows = "{:,}".format(paginator.count)

            return render(request, 'myroot/search.html',
                          {
                              'title': 'Search Results for: ' + str(fsearch),
                              'meta_desc': 'These are the list of search results based on your search text criteria.',
                              'data_pages': data_pages,
                              'page_range': page_range,
                              'totRows': totRows,
                              'q': fsearch
                           })
        else:
            return redirect('emptysearch')


def emptysearch_view(request):
    """Renders the empty search page."""
    if request.method == 'GET':
        return render(request, 'myroot/empty_search.html',
                      {'title': "Oops! Invalid Search.",
                       'meta_desc': """Either you forget to enter your search text criteria
                       or at least key-in the minimum of 3 characters for the search operation
                       to proceed. Thank You!"""})
