import json
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Export users to Keycloak-compatible JSON (without passwords)"

    def add_arguments(self, parser):
        parser.add_argument('--realm', type=str, default='myrealm', help='Keycloak realm name')
        parser.add_argument('--output', type=str, default='keycloak_users.json', help='Output file name')

    def handle(self, *args, **options):
        User = get_user_model()
        realm = options['realm']
        output_file = options['output']

        users_data = []
        for user in User.objects.all():
            users_data.append({
                "username": user.username,
                "email": user.email,
                "firstName": user.first_name,
                "lastName": user.last_name,
                "enabled": True,
                "emailVerified": True
            })

        export_data = {
            "realm": realm,
            "users": users_data
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(export_data, f, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Exported {len(users_data)} users to '{output_file}' for Keycloak realm '{realm}'"))