from django.urls import path
from . import views

app_name = "ai_jobseeker"

urlpatterns = [
    # Single unified route for both Resume Scan & Cover Letter
    path("analyze-resume/", views.analyze_resume, name="analyze_resume"),
    # Route matching template reverse call 'ai_jobseeker:cover_letter'
    path("cover-letter/", views.analyze_resume, name="cover_letter"),
]
