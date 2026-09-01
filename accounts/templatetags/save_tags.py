# accounts/templatetags/save_tags.py
from django import template

register = template.Library()


@register.filter
def has_saved(user, post):
    return post.saved_posts.filter(user=user).exists()
