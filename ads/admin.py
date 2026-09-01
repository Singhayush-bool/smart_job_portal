from django.contrib import admin
from .models import AdCampaign, Advertisement


@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "advertiser",
        "budget",
        "spent",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "start_date", "end_date")
    search_fields = ("title", "advertiser__username")


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "campaign",
        "ad_type",
        "impressions",
        "clicks",
        "cpc",
        "is_active",
    )
    list_filter = ("ad_type", "is_active", "campaign")
    search_fields = ("title", "destination_url")
