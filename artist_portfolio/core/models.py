from django.db import models
from django.utils.timezone import now


class Artwork(models.Model):
    """Model representing an artwork in the portfolio."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="gallery/")
    created_at = models.DateTimeField(auto_now_add=True) # Stores when the artwork was added

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    """A model for saving messages from a contact form."""
    name = models.CharField(max_length=255, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    message = models.TextField(verbose_name="Message")
    created_at = models.DateTimeField(default=now, verbose_name="Date and time of sending")
    is_processed = models.BooleanField(default=False, verbose_name="Processed")

    def __str__(self):
        return f"Message from {self.name} ({self.email}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Messages from the contact form"
        verbose_name_plural = "Messages from the contact form"
