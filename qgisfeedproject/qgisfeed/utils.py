# coding=utf-8
import logging
import unicodedata
import requests

from django.urls import reverse
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.contrib.gis.db.models import Model
from django.http import HttpRequest
from django.contrib.gis.geoip2 import GeoIP2

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


def parse_remote_addr(request: HttpRequest) -> str:
    """Extract client IP from request."""
    x_forwarded_for = request.headers.get("X-Forwarded-For", "")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0]
    return request.META.get("REMOTE_ADDR", "")

def get_location(remote_addr: str) -> str:
    """
        Return WKT location for the given remote_addr.
        This should be used only for the geofence feature
        and won't be saved in the database.
    """
    g = GeoIP2()
    if remote_addr:
        try:
            location = g.city(remote_addr)
            location_wkt = f"POINT({location['longitude']} {location['latitude']})"
            return location_wkt
        except Exception as e:
            return None
    return None


def trigger_password_reset(user_email: str) -> str:
    """
    Trigger a Keycloak password reset email for the given user.
    Sends a password reset action email using the Keycloak Admin API.
    """

    # We should get the token from Keycloak server
    keycloak_base_url = settings.KEYCLOAK_BASE_URL
    realm = settings.KEYCLOAK_REALM
    admin_username = settings.KEYCLOAK_ADMIN_USERNAME
    admin_password = settings.KEYCLOAK_ADMIN_PASSWORD
    client_id = settings.KEYCLOAK_CLIENT_ID

    token_url = f"{keycloak_base_url}/realms/master/protocol/openid-connect/token"
    token_data = {
        "grant_type": "password",
        "client_id": client_id,
        "username": admin_username,
        "password": admin_password
    }
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        access_token = token_response.json()["access_token"]

        # 2. Get user ID
        headers = {"Authorization": f"Bearer {access_token}"}
        user_resp = requests.get(
            f"{keycloak_base_url}/admin/realms/{realm}/users",
            headers=headers,
            params={"email": user_email}
        )
        user_resp.raise_for_status()
        users = user_resp.json()
        if not users:
            logger.error(f"No user found with email: {user_email}")
            return None
        user_id = users[0]["id"]

        # 3. Trigger execute-actions-email with redirectUri and lifespan
        reset_url = f"{keycloak_base_url}/admin/realms/{realm}/users/{user_id}/execute-actions-email"
        payload = ["UPDATE_PASSWORD"]
        params = {
            "lifespan": 1800,  # 30 minutes
            # "redirectUri": "https://your-frontend-app.com/after-reset"  # optional
        }
        resp = requests.put(reset_url, headers=headers, json=payload, params=params)
        resp.raise_for_status()

        logger.info("Password reset action triggered.")
        return resp.json()  # Return the response from Keycloak
    except Exception as e:
        logger.error(f"Error triggering password reset: {e}")
        return None
