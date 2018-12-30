from django.conf import settings
from django import forms
from django.forms import ModelForm

# Call myroot properties
from myroot.models import ContactUs


class Basic_CRUD_Create_Form(ModelForm):
    """
    Render the basic crud create form
    """
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your full name',
                                      'maxlength': '75'}))

    email = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your working email',
                                      'maxlength': '254'}))

    subject = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Enter your subject',
            'maxlength': '75'}))

    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control textarea',
                                     'placeholder': 'Enter your message'}))

    class Meta:
        model = ContactUs
        fields = ('full_name', 'email', 'subject', 'message')
