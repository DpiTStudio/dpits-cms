import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SiteSettings

obj = SiteSettings()
fields = ['twitter', 'pinterest', 'linkedin', 'contacts', 'whatsapp']
print("Checking fields in SiteSettings instance:")
for f in fields:
    has_attr = hasattr(obj, f)
    print(f"{f}: {has_attr}")
