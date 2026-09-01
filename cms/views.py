# cms/views.py
from django.shortcuts import get_object_or_404, redirect, render
from .forms import BlogPostForm
from .models import FAQ, BlogComment, BlogLike, BlogPost, StaticPage


def blog_list(request):
    blogs = BlogPost.objects.filter(is_published=True).order_by("-created_at")

    # Attach is_liked status for each blog to prevent template evaluation bugs
    for blog in blogs:
        if request.user.is_authenticated:
            blog.is_liked = blog.likes.filter(user=request.user).exists()
        else:
            blog.is_liked = False

    # Handle Frontend Blog Creation
    if request.method == "POST":
        if request.user.is_authenticated:
            form = BlogPostForm(request.POST, request.FILES)
            if form.is_valid():
                blog = form.save(commit=False)
                blog.author = request.user.get_full_name() or request.user.username
                blog.is_published = True
                blog.save()
                return redirect("cms:blog_list")
        else:
            return redirect("accounts:login")
    else:
        form = BlogPostForm()

    return render(request, "cms/blog_list.html", {"blogs": blogs, "form": form})


def blog_detail(request, slug):
    blog = get_object_or_404(BlogPost, slug=slug, is_published=True)

    # Check if current user has liked this post
    is_liked = False
    if request.user.is_authenticated:
        is_liked = blog.likes.filter(user=request.user).exists()

    # Handle Comment Submission
    if request.method == "POST":
        if request.user.is_authenticated:
            comment_text = request.POST.get("comment_content")
            if comment_text:
                BlogComment.objects.create(
                    blog=blog, user=request.user, content=comment_text
                )
                return redirect("cms:blog_detail", slug=blog.slug)
        else:
            return redirect("accounts:login")

    return render(request, "cms/blog_detail.html", {"blog": blog, "is_liked": is_liked})


def toggle_blog_like(request, slug):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    blog = get_object_or_404(BlogPost, slug=slug)
    like_qs = BlogLike.objects.filter(blog=blog, user=request.user)

    if like_qs.exists():
        like_qs.delete()  # Unlike
    else:
        BlogLike.objects.create(blog=blog, user=request.user)  # Like

    return redirect(request.META.get("HTTP_REFERER", "cms:blog_list"))


def faq_list(request):
    faqs = FAQ.objects.filter(is_active=True)
    return render(request, "cms/faq_list.html", {"faqs": faqs})


def static_page(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    return render(request, "cms/static_page.html", {"page": page})


def delete_blog_comment(request, comment_id):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    comment = get_object_or_404(BlogComment, id=comment_id)

    # Sirf wahi user comment delete kar sakega jisne wo comment kiya hai
    if comment.user == request.user:
        comment.delete()

    return redirect(request.META.get("HTTP_REFERER", "cms:blog_list"))
