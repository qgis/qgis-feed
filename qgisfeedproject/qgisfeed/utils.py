# coding=utf-8
import logging
import unicodedata

from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.gis.db.models import Model

logger = logging.getLogger('qgisfeed.admin')
QGISFEED_FROM_EMAIL = getattr(settings, 'QGISFEED_FROM_EMAIL', 'noreply@qgis.org')


def simplify(text: str) -> str:
    try:
        text = unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('utf-8')
    except:  # noqa
        pass
    return str(text)

  
def notify_reviewers(author, request, recipients, cc, obj):
    """Send notification emails"""
    body = f"""
        Hi, \r\n
        {author.username} asked you to review the feed entry available at {request.build_absolute_uri(reverse('feed_entry_update', args=(obj.pk,)))}
        Title: {obj.title}\r\n
        Your beloved QGIS Feed bot.
        """
    msg = EmailMultiAlternatives(
        'QGIS feed entry review requested by %s' % author.username,
        body,
        QGISFEED_FROM_EMAIL,
        recipients,
        cc=cc,
    )
    msg.send(fail_silently=True)

def get_field_max_length(ConfigurationModel: Model, field_name: str):
    try:
        config = ConfigurationModel.objects.get(field_name=field_name)
        return config.max_characters
    except ConfigurationModel.DoesNotExist:
        return 500
