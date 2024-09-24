#!/usr/bin/env python
""" manage.py - Django's command-line utility for administrative tasks. """

import os
import sys

if __name__ == '__main__':
    # If WEBSITE_HOSTNAME is defined as an environment variable, then we're running
    # on Azure App Service and should use the production settings.
    SETTINGS_MODULE = "tts.production" if 'WEBSITE_HOSTNAME' in os.environ else 'tts.settings'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', SETTINGS_MODULE)

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    execute_from_command_line(sys.argv)
