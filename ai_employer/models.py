from django.db import models


class AICandidateScreening(models.Model):
    # Link to application or job if existing in your accounts/jobs apps
    job_id = models.IntegerField()
    candidate_id = models.IntegerField()
    match_score = models.IntegerField(default=0)
    fraud_risk_level = models.CharField(
        max_length=20, default="LOW"
    )  # LOW, MEDIUM, HIGH
    summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
