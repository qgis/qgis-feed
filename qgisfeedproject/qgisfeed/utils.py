# coding=utf-8
import logging
import unicodedata

from django.urls import reverse
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger('qgisfeed.admin')
QGISFEED_FROM_EMAIL = getattr(settings, 'QGISFEED_FROM_EMAIL', 'noreply@qgis.org')


def simplify(text: str) -> str:
    try:
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    except:  # noqa
        pass
    return str(text)

  
def notify_admin(author, request, recipients, obj):
    """Send notification emails"""
    body = """
        User %s added a new entry.\r\n
        Title: %s\r\n
        Link: %s\r\n
        """ % (
            author.username,
            obj.title,
            request.build_absolute_uri(reverse('feed_entry_update', args=(obj.pk,)))
        )
    if settings.DEBUG:
        logger.debug("DEBUG is True: email not sent:\n %s" % body)
    else:
        send_mail(
            'A QGIS News Entry was added: %s' % obj.title,
            body,
            QGISFEED_FROM_EMAIL,
            recipients,
            fail_silently=True
        )
