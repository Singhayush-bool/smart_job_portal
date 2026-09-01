from django.urls import path
from . import views

app_name = "support"

urlpatterns = [
    path("", views.ticket_list, name="ticket_list"),
    path("create/", views.create_ticket, name="create_ticket"),
    path("t/<str:ticket_id>/", views.ticket_detail, name="ticket_detail"),
]
