from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render

from .models import AdCampaign, Advertisement


# =========================================================
# 1. ADVERTISER CAMPAIGN ANALYTICS DASHBOARD
# =========================================================
@login_required
def campaign_analytics(request):
    """Analytics dashboard showing Impressions, Clicks, CTR, Conversions, Revenue."""
    campaigns = (
        AdCampaign.objects.filter(advertiser=request.user)
        .prefetch_related("ads")
        .order_by("-created_at")
    )

    ads = Advertisement.objects.filter(campaign__advertiser=request.user)

    # Aggregated Stats
    total_impressions = ads.aggregate(Sum("impressions"))["impressions__sum"] or 0
    total_clicks = ads.aggregate(Sum("clicks"))["clicks__sum"] or 0
    total_conversions = ads.aggregate(Sum("conversions"))["conversions__sum"] or 0

    # Calculate overall CTR and Revenue
    overall_ctr = (
        round((total_clicks / total_impressions) * 100, 2)
        if total_impressions > 0
        else 0.0
    )
    total_revenue = sum(ad.total_revenue for ad in ads)

    return render(
        request,
        "ads/campaign_analytics.html",
        {
            "campaigns": campaigns,
            "ads": ads,
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "overall_ctr": overall_ctr,
            "total_revenue": total_revenue,
        },
    )


# =========================================================
# 2. AD CLICK TRACKER & REDIRECT
# =========================================================
def track_ad_click(request, ad_id):
    """Increments ad click count, updates campaign spend, and redirects to destination URL."""
    ad = get_object_or_404(Advertisement, id=ad_id)

    # Atomic Increment for clicks
    Advertisement.objects.filter(id=ad_id).update(clicks=F("clicks") + 1)

    # Deduct spend from campaign budget
    ad.campaign.spent = float(ad.campaign.spent) + float(ad.cpc)
    ad.campaign.save()

    return HttpResponseRedirect(ad.destination_url)
