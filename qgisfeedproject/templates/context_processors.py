from django.conf import settings

def settings_var(request):
    return {'MAIN_WEBSITE_URL': settings.MAIN_WEBSITE_URL}