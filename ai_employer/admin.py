from django.contrib import admin
from .models import AICandidateScreening


@admin.register(AICandidateScreening)
class AICandidateScreeningAdmin(admin.ModelAdmin):
    list_display = (
        "job_id",
        "candidate_id",
        "match_score",
        "fraud_risk_level",
        "created_at",
    )
    list_filter = ("fraud_risk_level", "created_at")
    search_fields = ("job_id", "candidate_id")
