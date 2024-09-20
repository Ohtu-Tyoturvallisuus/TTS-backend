from django.db import models
from django.contrib.auth.models import User

class Worksite(models.Model):
  name = models.CharField(max_length=100)
  location = models.CharField(max_length=100)
  
  def __str__(self):
    return self.name

class Survey(models.Model):
  worksite = models.ForeignKey(Worksite, on_delete=models.CASCADE)
  overseer = models.ForeignKey('auth.User', on_delete=models.CASCADE, null=False)
  title = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  created_at = models.DateTimeField()

  def __str__(self):
    return self.title

class RiskNote(models.Model):
  survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
  note = models.TextField()
  is_ok = models.BooleanField(default=False)
  is_not_relevant = models.BooleanField(default=False)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    status = "Kunnossa" if self.is_ok else "Ei koske" if self.is_not_relevant else "Vastaamatta"
    return f"{self.note} ({status} - {self.created_at})"

# class Profile(models.Model):
#     ROLE_CHOICES = [
#         ('overseer', 'Overseer'),
#         ('worker', 'Worker'),
#     ]
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES)

#     def __str__(self):
#         return f"{self.user.username} - {self.role}"