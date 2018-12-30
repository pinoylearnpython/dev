from django import forms
from django.forms import ModelForm

# Call bp properties
from bp.models import (Business, BusinessComment, BusinessReview,
                       BusinessInquiry)


class BusinessForm(ModelForm):
    """
    Render's the create ad form
    """
    company_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your company name',
                                      'maxlength': '125'}))

    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your company address',
                                      'maxlength': '255'}))

    tel_no = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Enter your company tel no',
            'maxlength': '75'}))

    fax_no = forms.CharField(required=False,
                             widget=forms.TextInput(attrs={
                                     'class': 'form-control', 'placeholder': 'Enter your company fax no',
                                     'maxlength': '75'}))

    email = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Enter your company email address',
            'maxlength': '254'}))

    website = forms.CharField(required=False,
                              widget=forms.TextInput(attrs={
                                      'class': 'form-control', 'placeholder': 'Enter your company website address',
                                      'maxlength': '255'}))

    office_hours = forms.CharField(required=False,
                                   widget=forms.TextInput(attrs={
                                           'class': 'form-control', 'placeholder': 'Enter your business hours',
                                           'maxlength': '75'}))

    short_desc = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control',
                                     'placeholder': 'Enter your profile meta description',
                                     'maxlength': '455'}))

    about = forms.CharField(required=False, widget=forms.Textarea(
        attrs={'class': 'form-control textarea',
               'placeholder': 'Write a content about your company history.'}))

    class Meta:
        model = Business
        fields = ('company_name', 'address', 'tel_no', 'fax_no', 'email',
                  'website', 'office_hours', 'short_desc', 'about')


class BPCommentForm(ModelForm):
    """
    Render our comment form for guest/users that will
    comment from a business profile page.
    """
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your full name',
                                      'maxlength': '75'}))

    comment = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control textarea',
                                     'placeholder': 'Enter your comment'}))

    class Meta:
        model = BusinessComment
        fields = ('full_name', 'comment')


class BPReviewForm(ModelForm):
    """
    Render our business review form for guest/users that will
    give business review from a business profile page.
    """
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your full name',
                                      'maxlength': '75',
                                      'id': 'id_full_name_review',
                                      'name': 'id_full_name_review'}))

    email = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': 'Enter your email',
                                                          'maxlength': '80',
                                                          'id': 'id_email_review',
                                                          'name': 'id_email_review'}))

    review = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control textarea',
                                     'placeholder': 'Enter your business review'}))

    class Meta:
        model = BusinessReview
        fields = ('full_name', 'email', 'review')


class BPInquiryForm(ModelForm):
    """
    Render our business inquiry form for guest/users that will
    submit an inquiry from a business profile page.
    """
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control',
                                      'placeholder': 'Enter your full name',
                                      'maxlength': '75',
                                      'id': 'id_full_name_inquiry',
                                      'name': 'id_full_name_inquiry'}))

    email = forms.CharField(required=False,
                            widget=forms.TextInput(attrs={'class': 'form-control',
                                                          'placeholder': 'Enter your email',
                                                          'maxlength': '80',
                                                          'id': 'id_email_inquiry',
                                                          'name': 'id_email_inquiry'}))

    subject = forms.CharField(
            widget=forms.TextInput(attrs={'class': 'form-control',
                                          'placeholder': 'Enter your full name',
                                          'maxlength': '75'}))

    inquiry = forms.CharField(
            widget=forms.Textarea(attrs={'class': 'form-control textarea',
                                         'placeholder': 'Enter your business inquiry'}))

    class Meta:
        model = BusinessInquiry
        fields = ('full_name', 'email', 'subject', 'inquiry')
