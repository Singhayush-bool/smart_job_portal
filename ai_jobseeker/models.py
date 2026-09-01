from django.conf import settings
from django.db import models


class AIResumeAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ats_score = models.IntegerField(default=0)
    resume_score = models.IntegerField(default=0)
    skill_gaps = models.JSONField(default=list)
    suggested_improvements = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)


class AICoverLetter(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    generated_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
