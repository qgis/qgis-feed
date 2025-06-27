from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
# from django.contrib.sites.models import Site
import json

class Command(BaseCommand):
    help = 'Add or update a Keycloak OpenID Connect social application using interactive input'

    def handle(self, *args, **options):
        # Display header
        self.stdout.write(self.style.MIGRATE_HEADING("Keycloak Social Application Setup"))
        self.stdout.write("This will create or update a Keycloak OpenID Connect social application.\n")

        # Get input values
        client_id = input("Enter Keycloak Client ID: ")
        secret = input("Enter Keycloak Client Secret: ")
        domain = input("Enter Keycloak Domain (e.g., http://localhost or https://auth.example.com): ")
        realm = input("Enter Keycloak Realm Name (e.g., qgis): ")

        provider = 'openid_connect'
        provider_id = 'keycloak'
        name = 'Keycloak'

        # Get the default site
        # site = Site.objects.get_current()

        # Create or update the social app
        
        social_app, created = SocialApp.objects.update_or_create(
            provider=provider,
            defaults={
                'provider_id': provider_id,
            }
        )

        social_app.name = name
        social_app.client_id = client_id
        social_app.secret = secret
        social_app.settings = {
            "server_url": f"{domain}/realms/{realm}/.well-known/openid-configuration"
        }
        social_app.save()

        # Add the site to the social app if not already present
        # if site not in social_app.sites.all():
        #     social_app.sites.add(site)

        action = 'Created' if created else 'Updated'
        self.stdout.write("\n" + self.style.SUCCESS(
            f'{action} Keycloak social application with:'
        ))
        self.stdout.write(f"- Client ID: {client_id}")
        self.stdout.write(f"- Domain: {domain}")
        self.stdout.write(f"- Realm: {realm}")
        self.stdout.write(f"- OpenID Config URL: {domain}/realms/{realm}/.well-known/openid-configuration")