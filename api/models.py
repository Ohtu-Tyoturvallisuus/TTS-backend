""" api/models.py """

from django.db import models

class Project(models.Model):
    """Class for Project model"""
    project_id = models.CharField(max_length=100, unique=True)
    project_name = models.CharField(max_length=255)
    dimension_display_value = models.CharField(max_length=255)
    project_group = models.CharField(max_length=100)

    def __str__(self):
        return str(self.project_name)

class Survey(models.Model):
    """Class for Survey model"""
    project = models.ForeignKey(Project, related_name="surveys", on_delete=models.CASCADE)
    description = models.TextField(max_length=250)
    task = models.TextField(max_length=50)
    scaffold_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.task} - {self.scaffold_type}"

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
