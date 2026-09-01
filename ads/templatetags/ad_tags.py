from django import template
from django.db.models import F

from ads.models import Advertisement

register = template.Library()


@register.inclusion_tag("ads/components/ad_unit.html")
def render_ad(ad_type):
    """Fetches an active ad of given type and automatically logs an Impression."""
    ad = (
        Advertisement.objects.filter(
            ad_type=ad_type, is_active=True, campaign__status="active"
        )
        .order_by("?")
        .first()
    )

    if ad:
        # Increment Impression count
        Advertisement.objects.filter(id=ad.id).update(impressions=F("impressions") + 1)

    return {"ad": ad}
