from django import template
import os.path
from django.conf import settings

register = template.Library()

@register.simple_tag
def get_sustaining_members_section():
    """
    Get the Sustaining members HTML from the template file
    """
    template_path = os.path.join(
      os.path.dirname(settings.SITE_ROOT),
      'templates/layouts/sustaining_members.html'
    )
    try:
        with open(template_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        return ""
