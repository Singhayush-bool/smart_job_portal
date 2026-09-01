from django.contrib import admin
from .models import TicketCategory, SupportTicket, TicketReply


class TicketReplyInline(admin.TabularInline):
    model = TicketReply
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description")
    search_fields = ("name",)


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        "ticket_id",
        "subject",
        "user",
        "category",
        "priority",
        "status",
        "assigned_to",
        "created_at",
    )
    list_filter = ("status", "priority", "category", "created_at")
    search_fields = (
        "ticket_id",
        "subject",
        "description",
        "user__username",
        "user__email",
    )
    raw_id_fields = ("user", "assigned_to")
    inlines = [TicketReplyInline]


@admin.register(TicketReply)
class TicketReplyAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "user", "created_at")
    search_fields = ("message", "user__username")
    raw_id_fields = ("ticket", "user")
