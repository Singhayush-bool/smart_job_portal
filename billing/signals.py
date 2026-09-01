from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Subscription, SubscriptionUsage


@receiver(post_save, sender=Subscription)
def create_subscription_usage(sender, instance, created, **kwargs):
    if created:
        SubscriptionUsage.objects.create(subscription=instance)
