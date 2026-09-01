from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list, name="notification_list"),
    path("<int:pk>/read/", views.mark_as_read, name="mark_as_read"),
    path("mark-all-read/", views.mark_all_as_read, name="mark_all_as_read"),
    path(
        "accept/<int:pk>/",
        views.accept_connection_notification,
        name="accept_connection",
    ),
    path(
        "reject/<int:pk>/",
        views.reject_connection_notification,
        name="reject_connection",
    ),
]
