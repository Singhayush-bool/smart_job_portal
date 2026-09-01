from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from accounts.models import Job
from .models import BlogPost


class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Job.objects.filter(is_approved=True, is_active=True)

    def lastmod(self, obj):
        return obj.created_at

    def location(self, obj):
        return reverse("accounts:job_detail", args=[obj.id])


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("cms:blog_detail", args=[obj.slug])


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return [
            "accounts:job_list",
            "cms:faq_list",
            "cms:blog_list",
        ]

    def location(self, item):
        return reverse(item)
