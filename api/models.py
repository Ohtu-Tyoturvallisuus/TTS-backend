from django.db import models
from django.contrib.auth.models import User

class Worksite(models.Model):
  name = models.CharField(max_length=100)
  location = models.CharField(max_length=100)
  
  def __str__(self):
    return self.name

class Survey(models.Model):
  worksite = models.ForeignKey(Worksite, related_name='surveys', on_delete=models.CASCADE)
  overseer = models.ForeignKey('auth.User', related_name='surveys', on_delete=models.CASCADE, null=True)
  title = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)
  risks = models.JSONField(default="{}")

  def __str__(self):
    return self.title

class RiskNote(models.Model):
  survey = models.ForeignKey(Survey, related_name="risk_notes", on_delete=models.CASCADE)
  note = models.TextField()
  description = models.TextField(blank=True)
  status = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.note} ({self.created_at})"
