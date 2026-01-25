"""
Settings module initialization.
Loads the appropriate settings based on DJANGO_ENV environment variable.
"""
import os

env = os.getenv('DJANGO_ENV', 'development')

if env == 'production':
    from .production import *
elif env == 'test':
    from .test import *
else:
    from .development import *
