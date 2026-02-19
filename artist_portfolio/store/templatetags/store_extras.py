from django import template

register = template.Library()


@register.filter
def image_url_or(field_file, fallback_url):
    """
    Safely returns ImageField url, or fallback_url if file is missing.
    """
    try:
        if field_file and getattr(field_file, "name", ""):
            return field_file.url
    except (ValueError, AttributeError):
        pass
    return fallback_url
