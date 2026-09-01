from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Conversation, Message
from .forms import MessageForm
from django.contrib.auth import get_user_model

User = get_user_model()


from django.db.models import Q
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def inbox(request):
    user = request.user
    query = request.GET.get('q', '')
    
    # Existing conversations
    conversations = Conversation.objects.filter(
        Q(job_seeker=user) | Q(recruiter=user)
    ).order_by("-updated_at")

    # Search functionality to find other users to message
    search_users = []
    if query:
        search_users = User.objects.exclude(id=user.id).filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )[:10]

    return render(request, "messaging/inbox.html", {
        "conversations": conversations,
        "query": query,
        "search_users": search_users
    })

@login_required
def chat_detail(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)

    if (
        request.user != conversation.job_seeker
        and request.user != conversation.recruiter
    ):
        return redirect("messaging:inbox")

    # Mark unread messages as read
    unread_msgs = conversation.messages.exclude(sender=request.user).filter(
        is_read=False
    )
    unread_msgs.update(is_read=True)

    messages = conversation.messages.all()

    if request.method == "POST":
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.conversation = conversation
            new_message.sender = request.user
            new_message.save()
            conversation.save()  # Triggers updated_at auto_now
            return redirect("messaging:chat_detail", conversation_id=conversation.id)
    else:
        form = MessageForm()

    other_user = (
        conversation.recruiter
        if request.user == conversation.job_seeker
        else conversation.job_seeker
    )

    context = {
        "conversation": conversation,
        "messages": messages,
        "form": form,
        "other_user": other_user,
    }
    return render(request, "messaging/chat_detail.html", context)


@login_required
def start_conversation(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    # Determine user roles relative to conversation
    if getattr(request, "role", None) == "EMPLOYER" or request.user.is_staff:
        recruiter = request.user
        job_seeker = other_user
    else:
        job_seeker = request.user
        recruiter = other_user

    conversation, created = Conversation.objects.get_or_create(
        job_seeker=job_seeker, recruiter=recruiter
    )

    return redirect("messaging:chat_detail", conversation_id=conversation.id)
