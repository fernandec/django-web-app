"""
WSGI config for gallery project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application


sys.path.append('/home/bf/projects/django-web-app/gallery')
sys.path.append('/home/bf/projects/django-web-app/gallery/gallery')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gallery.settings')

application = get_wsgi_application()
