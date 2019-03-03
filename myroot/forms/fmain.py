from django.conf import settings
from django import forms
from django.forms import ModelForm

# For Django's built-in User Auth System
from django.contrib.auth.models import User
from django.contrib.auth.forms import (UserCreationForm, AuthenticationForm,
                                       PasswordResetForm, SetPasswordForm)

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


class SignUpForm(UserCreationForm):
    """Render the signup form for new user registration."""
    username = forms.CharField(
        max_length=254, widget=forms.TextInput(
            {'class': 'form-control',
                'placeholder': 'Enter your user name'})
    )

    email = forms.EmailField(
        max_length=254, widget=forms.TextInput(
            {'class': 'form-control',
                'placeholder': 'Enter your email address'})
    )

    password1 = forms.CharField(
        max_length=50, widget=forms.PasswordInput({
            'class': 'form-control',
            'placeholder': 'Password'})
    )

    password2 = forms.CharField(
        max_length=50, widget=forms.PasswordInput(
            {'class': 'form-control',
                'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class LoginAuthenticationForm(AuthenticationForm):
    """ Provide login auth form for users to sign in to our site """
    username = forms.CharField(
        max_length=254, widget=forms.TextInput(
            {'class': 'form-control',
             'placeholder': 'Enter your username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput({
            'class': 'form-control',
            'placeholder': 'Enter your password'})
    )


class PasswordResetForm(PasswordResetForm):
    """
    Provide forgot password functionality and be able to
    reset the user's new password by themselves.
    """
    email = forms.EmailField(
        max_length=254, widget=forms.TextInput(
            {'class': 'form-control',
                'placeholder': 'Enter your email address'})
    )


class PasswordResetConfirmForm(SetPasswordForm):
    """
    Upon user checks their mailbox and click on the reset new password link
    provided for them, this form will render and then
    start resetting a new password.
    """
    new_password1 = forms.CharField(
        widget=forms.PasswordInput({
            'class': 'form-control',
            'placeholder': 'Password'}))
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(
            {'class': 'form-control',
                'placeholder': 'Confirm Password'}))

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')


class ChangePasswordForm(SetPasswordForm):
    """
    Custom change password from the dashboard access.
    """
    new_password1 = forms.CharField(
        max_length=50, widget=forms.PasswordInput({
            'class': 'form-control',
            'placeholder': 'Password'})
    )

    new_password2 = forms.CharField(
        max_length=50, widget=forms.PasswordInput(
            {'class': 'form-control',
                'placeholder': 'Confirm Password'})
    )

    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')
