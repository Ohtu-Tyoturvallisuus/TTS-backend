""" api/admin.py """

from django.contrib import admin
from .models import Project, Survey, RiskNote

admin.site.register(Project)
admin.site.register(Survey)
admin.site.register(RiskNote)
