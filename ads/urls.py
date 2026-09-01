from django.urls import path
from . import views

app_name = "ads"  # <-- YE LINE INCLUDED HONI CHAHIYE

urlpatterns = [
    path("analytics/", views.campaign_analytics, name="campaign_analytics"),
    path("click/<int:ad_id>/", views.track_ad_click, name="track_ad_click"),
]
