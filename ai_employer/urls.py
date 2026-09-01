from django.urls import path
from . import views

app_name = "ai_employer"

urlpatterns = [
    path("generate-jd/", views.generate_job_description, name="generate_jd"),
]
