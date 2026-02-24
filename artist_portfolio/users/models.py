from django.db import models
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField


class UserProfile(models.Model):
    """
    A user profile model that contains additional information,
    such as phone number, country, address, and avatar.
    """
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="userprofile"
    )
    phone = PhoneNumberField(
        blank=True, null=True, region="UA"
    )
    country = CountryField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(
        upload_to="profile_pictures/",
        blank=True,
        null=True,
        default="profile_pictures/default.png",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def full_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    class Meta:
        verbose_name = "UserProfile"
        verbose_name_plural = "UserProfiles"


class UserOTP(TOTPDevice):
    """
    A model for two-factor authentication (OTP) based on TOTP.
    Inherits from django-otp for integration with OTP devices.
    """
    pass


def is_owner(self):
    return self.groups.filter(name="Owner").exists()


User.is_owner = property(is_owner)
