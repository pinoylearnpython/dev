from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from django.http import Http404

# Call myroot properties
from myroot.forms.fmain import Basic_CRUD_Create_Form
from myroot.views.vfunctions import dict_alert_msg
from myroot.models import ContactUs


def hello_world_view(request):
    """Renders the Hello World page."""
    if request.method == 'GET':
        return render(request, 'myroot/hello_world.html',
                      {'title': 'Hello World!',
                       'meta_desc': "The complete step-by-step guide in displaying Hello World using Django Template with NGINX guide to set up a new website from scratch.",
                       'BASE_URL': settings.BASE_URL})


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
