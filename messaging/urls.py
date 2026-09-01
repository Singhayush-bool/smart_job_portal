from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("inbox/", views.inbox, name="inbox"),
    path("c/<int:conversation_id>/", views.chat_detail, name="chat_detail"),
    path("start/<int:user_id>/", views.start_conversation, name="start_conversation"),
]
