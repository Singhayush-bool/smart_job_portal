from django.core.management.base import BaseCommand
from django.utils import timezone
from billing.models import Subscription


class Command(BaseCommand):
    help = "Check and expire subscriptions that passed current_period_end"

    def handle(self, *args, **options):
        now = timezone.now()
        expired_subs = Subscription.objects.filter(
            status="active", current_period_end__lt=now
        )
        count = expired_subs.count()
        expired_subs.update(status="expired")

        self.stdout.write(
            self.style.SUCCESS(f"Successfully expired {count} overdue subscriptions.")
        )
