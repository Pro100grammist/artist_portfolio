from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from phonenumber_field.formfields import PhoneNumberField
from django_countries.widgets import CountrySelectWidget

from .models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    """Form for user registration"""

    username = forms.CharField(
        label="Username",
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "pattern": "[a-zA-Z0-9@./+/-/_]*",  # Restrictions on characters in the username
                "placeholder": "Enter your username",
            }
        ),
    )
    first_name = forms.CharField(
        label="First Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your first name"}),
    )
    last_name = forms.CharField(
        label="Last Name",
        widget=forms.TextInput(attrs={"placeholder": "Enter your last name"}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email address"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Enter your password"}),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={"placeholder": "Confirm your password"}),
    )

    class Meta:
        """
        The form works with the User model and registration fields.
        """
        model = User
        fields = ["username", "first_name", "last_name", "email"]

    def clean_password2(self):
        """Check if passwords match"""
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords do not match!")
        return password2


class UserProfileUpdateForm(forms.ModelForm):
    """
    A form for updating a user's profile.
    """
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-control"})
    )

    class Meta:
        """
        the form works with the UserProfile model and updates the corresponding fields.
        """
        model = UserProfile
        fields = ["avatar", "phone", "country", "address"]

    def __init__(self, *args, **kwargs):
        """
        initializing the form with the current user data.
        """
        user = kwargs.pop("user", None)  # Getting a user
        super().__init__(*args, **kwargs)

        # Fill in the initial field values from the user data
        if user:
            self.fields["username"].initial = user.username
            self.fields["first_name"].initial = user.first_name
            self.fields["last_name"].initial = user.last_name
            self.fields["email"].initial = user.email


class CustomAuthenticationForm(AuthenticationForm):
    """
    A slightly customized form of user authentication.
    """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"placeholder": "Username", "class": "form-control"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "class": "form-control"}
        )
    )
