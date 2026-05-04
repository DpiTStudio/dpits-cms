import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from django.template.loader import render_to_string
from django.test import RequestFactory

rf = RequestFactory()
request = rf.get('/')

# Mock some context variables that are expected by base.html
context = {
    'request': request,
    'site_settings': {'logo_text': 'Test', 'short_description': 'Test'},
    'statistics_banners': {'head': '', 'body_start': ''},
    'cart': []
}

templates_to_test = [
    '_base.html',
    'main/home.html',
    'news/list.html',
    'portfolio/list.html'
]

errors = 0
for tpl in templates_to_test:
    try:
        render_to_string(tpl, context)
        print(f"[OK] {tpl}")
    except Exception as e:
        print(f"[FAIL] {tpl}: {e}")
        errors += 1

if errors == 0:
    print("All templates rendered successfully!")
else:
    print(f"Found {errors} template errors.")
