# __init__.py

from django.apps import apps

from einvestment import settings

# Ilgari yuklangan ilovalar
if not apps.ready:
    apps.populate(settings.INSTALLED_APPS)
