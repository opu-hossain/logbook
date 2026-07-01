from django import template

register = template.Library()


@register.filter
def in_folder(active_slug, folder_path):
    """True if active_slug is this folder's own page, or nested inside it."""
    if not active_slug or not folder_path:
        return False
    return active_slug == folder_path or active_slug.startswith(folder_path + "/")
