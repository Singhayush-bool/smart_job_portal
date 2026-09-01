from django.urls import path
from . import views

app_name = "integrations"

urlpatterns = [
    path("test/", views.test_panel_view, name="test_panel"),
    path("notify/whatsapp/", views.notify_whatsapp, name="notify_whatsapp"),
    path("notify/push/", views.notify_push, name="notify_push"),
    path("upload/media/", views.upload_media, name="upload_media"),
]
