from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SupportTicket, TicketCategory
from .forms import TicketForm, TicketReplyForm


@login_required
def ticket_list(request):
    """User ki apni open aur closed tickets"""
    if request.user.is_staff:
        tickets = SupportTicket.objects.all().order_by("-created_at")
    else:
        tickets = SupportTicket.objects.filter(user=request.user).order_by(
            "-created_at"
        )

    return render(request, "support/ticket_list.html", {"tickets": tickets})


@login_required
def create_ticket(request):
    """Nayi support ticket create karne ke liye"""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            # Yaha In-App ya Email notification bhej sakte hain admin ko
            return redirect("support:ticket_detail", ticket_id=ticket.ticket_id)
    else:
        form = TicketForm()

    return render(request, "support/create_ticket.html", {"form": form})


@login_required
def ticket_detail(request, ticket_id):
    """Ticket ki detail aur reply karne ka interface"""
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)

    # Security: Staff ya ticket ka owner hi dekh sakta hai
    if not request.user.is_staff and ticket.user != request.user:
        return redirect("support:ticket_list")

    replies = ticket.replies.all()

    if request.method == "POST":
        form = TicketReplyForm(request.POST, request.FILES)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.ticket = ticket
            reply.user = request.user
            reply.save()
            return redirect("support:ticket_detail", ticket_id=ticket.ticket_id)
    else:
        form = TicketReplyForm()

    context = {"ticket": ticket, "replies": replies, "form": form}
    return render(request, "support/ticket_detail.html", context)
