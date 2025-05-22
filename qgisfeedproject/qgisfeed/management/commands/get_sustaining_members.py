from django.core.management.base import BaseCommand
import requests
from bs4 import BeautifulSoup
from django.conf import settings
import os

class Command(BaseCommand):
    help = "Get the Sustaining members HTML section from the new website"

    def handle(self, *args, **options):
        try:
            url = 'https://qgis.org'
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract the section by the specified class name
            section = soup.select_one('section.section')

            if section:
                html_content = section.prettify().replace("Â¶", "¶")
                template_path = os.path.join(
                    os.path.dirname(settings.SITE_ROOT),
                    'templates/layouts/sustaining_members.html'
                )
                with open(template_path, 'w') as f:
                    f.write(html_content)
                self.stdout.write(self.style.SUCCESS(f"Section saved to {template_path}"))
            else:
                self.stdout.write(self.style.WARNING("Section not found"))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"Request error: {e}"))
