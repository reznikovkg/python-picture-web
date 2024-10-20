"""
ASGI config for python_picture_web project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from pathlib import Path

from django.core.asgi import get_asgi_application
from dotenv import load_dotenv

from .initializer import Initializer

env_path = os.path.join(Path(__file__).resolve().parent.parent, ".env")
if os.path.exists(env_path):
    load_dotenv(env_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'python_picture_web.settings')

application = get_asgi_application()

Initializer().execute()
