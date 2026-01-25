"""
Development settings.
"""
from .base import *

DEBUG = True

# Development-specific apps
# INSTALLED_APPS += [
#     'django_extensions',  # Optional: useful development tools
# ]

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Email backend for development (console output)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable HTTPS redirect in development
SECURE_SSL_REDIRECT = False

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
