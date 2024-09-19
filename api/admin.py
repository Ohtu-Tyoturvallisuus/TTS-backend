from django.contrib import admin
from .models import Worksite, Survey, RiskNote

admin.site.register(Worksite)
admin.site.register(Survey)
admin.site.register(RiskNote)
