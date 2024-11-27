""" api/models.py """

import uuid
from django.db import models
from django.core.exceptions import ValidationError

class Project(models.Model):
    """Class for Project model"""
    project_id = models.CharField(max_length=100, unique=True)
    data_area_id = models.CharField(max_length=100)
    project_name = models.CharField(max_length=255)
    dimension_display_value = models.CharField(max_length=255)
    worker_responsible_personnel_number = models.CharField(max_length=100)
    customer_account = models.CharField(max_length=100)

    def __str__(self):
        return str(self.project_name)

class Survey(models.Model):
    """Class for Survey model"""
    project = models.ForeignKey(Project, related_name="surveys", on_delete=models.CASCADE)
    description = models.TextField(max_length=250)
    task = models.JSONField()
    scaffold_type = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{', '.join(self.task)} - {', '.join(self.scaffold_type)}"

    def clean(self):
        errors = {}
        if not self.task:
            errors['task'] = "Task field cannot be empty."
        if not self.scaffold_type:
            errors['scaffold_type'] = "Scaffolding type field cannot be empty."

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class RiskNote(models.Model):
    """Class for RiskNote model"""
    survey = models.ForeignKey(Survey, related_name="risk_notes", on_delete=models.CASCADE)
    note = models.TextField()
    description = models.TextField(blank=True)
    status = models.TextField(blank=True)
    risk_type = models.TextField(blank=True)
    images = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.note} ({self.created_at})"

class Account(models.Model):
    """Class for Account model"""
    username = models.CharField(max_length=150)
    user_id = models.CharField(max_length=64, unique=True, default=uuid.uuid4().hex)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.user_id})"

class AccountSurvey(models.Model):
    """Intermediate model to represent a user's filled survey"""
    account = models.ForeignKey(Account, related_name="filled_surveys", on_delete=models.CASCADE)
    survey = models.ForeignKey(Survey, related_name="filled_by", on_delete=models.CASCADE)
    filled_at = models.DateTimeField(auto_now_add=True)
