import os
import sys
import django

sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from main.models import SiteSettings

fields = [f.name for f in SiteSettings._meta.get_fields()]
print("Fields in SiteSettings:")
for f in fields:
    print(f"- {f}")
