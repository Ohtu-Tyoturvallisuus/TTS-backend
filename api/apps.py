""" api/apps.py """

from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Class for ApiConfig"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
