from django.contrib import admin

from .models import JobView, Placement, ProfileView, ResumeDownload


@admin.register(JobView)
class JobViewAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "user", "ip_address", "created_at")
    list_filter = ("created_at",)
    search_fields = ("job__title", "user__username", "ip_address")
    ordering = ("-created_at",)


@admin.register(ProfileView)
class ProfileViewAdmin(admin.ModelAdmin):
    list_display = ("id", "profile", "viewer", "created_at")
    list_filter = ("created_at",)
    search_fields = ("profile__user__username", "viewer__username")
    ordering = ("-created_at",)


@admin.register(Placement)
class PlacementAdmin(admin.ModelAdmin):
    list_display = ("id", "application", "hired_at", "cost_per_hire")
    list_filter = ("hired_at",)
    search_fields = (
        "application__applicant__username",
        "application__job__title",
    )
    ordering = ("-hired_at",)


@admin.register(ResumeDownload)
class ResumeDownloadAdmin(admin.ModelAdmin):
    list_display = ("id", "job_seeker", "downloaded_by", "created_at")
    list_filter = ("created_at",)
    search_fields = ("job_seeker__username", "downloaded_by__username")
    ordering = ("-created_at",)
