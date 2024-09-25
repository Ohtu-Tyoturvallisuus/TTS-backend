""" api/models.py """

from django.db import models
from django.contrib.auth import get_user_model

class Worksite(models.Model):
    """Class for Worksite model"""
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

    def __str__(self):
        return str(self.name)

class Survey(models.Model):
    """Class for Survey model"""
    worksite = models.ForeignKey(Worksite, related_name='surveys', on_delete=models.CASCADE)
    overseer = models.ForeignKey(get_user_model(), related_name='surveys', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.title)

class RiskNote(models.Model):
    """Class for RiskNote model"""
    survey = models.ForeignKey(Survey, related_name="risk_notes", on_delete=models.CASCADE)
    note = models.TextField()
    description = models.TextField(blank=True)
    status = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note} ({self.created_at})"
