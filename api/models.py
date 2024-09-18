from django.db import models

class Worksite(models.Model):
  name = models.CharField(max_length=100)
  location = models.CharField(max_length=100)
  
  def __str__(self):
    return self.name

class RiskSurvey(models.Model):
  worksite = models.ForeignKey(Worksite, on_delete=models.SET_NULL, null=True, blank=True)
  title = models.CharField(max_length=100)
  description = models.TextField(blank=True)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return self.title

class RiskNote(models.Model):
  survey = models.ForeignKey(RiskSurvey, on_delete=models.CASCADE)
  note = models.TextField()
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.note} ({self.created_at})"


# class Worker(models.Model):
#   name = models.CharField(max_length=100)
#   worksite = models.ForeignKey(Worksite, on_delete=models.CASCADE)

#   def __str__(self):
#     return self.name
