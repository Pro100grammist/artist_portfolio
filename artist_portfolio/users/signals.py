from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User

from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically creates a user profile after user registration,
    but does not create a profile for superusers.

    :param sender: The class of the model that triggers the signal.
    :param instance: An instance of the user.
    :param created: Boolean value indicating whether the user was created.
    """
    if created and not instance.is_superuser:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Saves the associated user profile after updating the User model.
    """
    if not instance.is_superuser and hasattr(instance, "userprofile"):  # Check for a profile
        instance.userprofile.save()
