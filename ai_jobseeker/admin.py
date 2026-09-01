from django.contrib import admin
from .models import AICoverLetter, AIResumeAnalysis


@admin.register(AIResumeAnalysis)
class AIResumeAnalysisAdmin(admin.ModelAdmin):
    list_display = ("user", "ats_score", "resume_score", "created_at")
    search_fields = ("user__username", "user__email")
    list_filter = ("created_at",)


@admin.register(AICoverLetter)
class AICoverLetterAdmin(admin.ModelAdmin):
    list_display = ("user", "job_title", "company_name", "created_at")
    search_fields = ("user__username", "job_title", "company_name")
    list_filter = ("created_at",)
