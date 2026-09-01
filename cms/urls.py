# cms/urls.py
from django.urls import path
from . import views

app_name = "cms"

urlpatterns = [
    path("blogs/", views.blog_list, name="blog_list"),
    path("blogs/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("blogs/<slug:slug>/like/", views.toggle_blog_like, name="toggle_blog_like"),
    path("faqs/", views.faq_list, name="faq_list"),
    path("pages/<slug:slug>/", views.static_page, name="static_page"),
    path(
        "comment/<int:comment_id>/delete/",
        views.delete_blog_comment,
        name="delete_blog_comment",
    ),
]
