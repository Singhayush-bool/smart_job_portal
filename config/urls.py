from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

# CMS Sitemaps import
from cms.sitemaps import BlogSitemap, JobSitemap, StaticViewSitemap

# Sitemap Dictionary Configuration
sitemaps = {
    "jobs": JobSitemap,
    "blogs": BlogSitemap,
    "static": StaticViewSitemap,
}


# Dynamic robots.txt View
def robots_txt(request):
    content = """User-agent: *
Disallow: /admin/
Disallow: /accounts/dashboard/
Disallow: /billing/

Sitemap: {}://{}/sitemap.xml
""".format(request.scheme, request.get_host())
    return HttpResponse(content, content_type="text/plain")


urlpatterns = [
    path("admin/", admin.site.urls),
    # Baaki sabhi apps ke paths pehle honge
    path("billing/", include("billing.urls")),
    path("ads/", include("ads.urls")),
    path("cms/", include("cms.urls")),
    path("analytics/", include("analytics.urls")),
    path("messages/", include("messaging.urls")),
    path("support/", include("support.urls")),
    path("notifications/", include("notifications.urls")),
    path("ai/jobseeker/", include("ai_jobseeker.urls", namespace="ai_jobseeker")),
    path("ai/employer/", include("ai_employer.urls", namespace="ai_employer")),
    path(
        "api/v1/integrations/",
        include(("integrations.urls", "integrations"), namespace="integrations"),
    ),
    # 'accounts.urls' ko hamesha ANTIM (last) mein rakhein
    path("", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
