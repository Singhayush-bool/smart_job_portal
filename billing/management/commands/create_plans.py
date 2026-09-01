from django.core.management.base import BaseCommand

from billing.models import SubscriptionPlan


class Command(BaseCommand):

    help = "Create default subscription plans"

    def handle(self, *args, **kwargs):

        plans = [
            # =================================================
            # JOB SEEKER - FREE
            # =================================================
            {
                "name": "Free",
                "slug": "job-seeker-free",
                "user_type": "job_seeker",
                "plan_type": "free",
                "description": "Basic job seeker plan",
                "price_monthly": 0,
                "price_yearly": 0,
                "job_post_limit": 0,
                "resume_download_limit": 0,
                "featured_jobs": False,
                "company_branding": False,
                "analytics": False,
                "priority_support": False,
            },
            # =================================================
            # JOB SEEKER - PREMIUM
            # =================================================
            {
                "name": "Premium",
                "slug": "job-seeker-premium",
                "user_type": "job_seeker",
                "plan_type": "premium",
                "description": "Premium plan for active job seekers",
                "price_monthly": 299,
                "price_yearly": 2999,
                "job_post_limit": 0,
                "resume_download_limit": 10,
                "featured_jobs": False,
                "company_branding": False,
                "analytics": True,
                "priority_support": False,
            },
            # =================================================
            # JOB SEEKER - PRO
            # =================================================
            {
                "name": "Pro",
                "slug": "job-seeker-pro",
                "user_type": "job_seeker",
                "plan_type": "pro",
                "description": "Advanced plan for professional job seekers",
                "price_monthly": 599,
                "price_yearly": 5999,
                "job_post_limit": 0,
                "resume_download_limit": 30,
                "featured_jobs": True,
                "company_branding": False,
                "analytics": True,
                "priority_support": True,
            },
            # =================================================
            # EMPLOYER - STARTER
            # =================================================
            {
                "name": "Starter",
                "slug": "employer-starter",
                "user_type": "employer",
                "plan_type": "starter",
                "description": "Starter plan for small employers",
                "price_monthly": 999,
                "price_yearly": 9999,
                "job_post_limit": 5,
                "resume_download_limit": 20,
                "featured_jobs": False,
                "company_branding": True,
                "analytics": False,
                "priority_support": False,
            },
            # =================================================
            # EMPLOYER - BUSINESS
            # =================================================
            {
                "name": "Business",
                "slug": "employer-business",
                "user_type": "employer",
                "plan_type": "business",
                "description": "Business plan for growing companies",
                "price_monthly": 2499,
                "price_yearly": 24999,
                "job_post_limit": 25,
                "resume_download_limit": 100,
                "featured_jobs": True,
                "company_branding": True,
                "analytics": True,
                "priority_support": False,
            },
            # =================================================
            # EMPLOYER - ENTERPRISE
            # =================================================
            {
                "name": "Enterprise",
                "slug": "employer-enterprise",
                "user_type": "employer",
                "plan_type": "enterprise",
                "description": "Enterprise plan for large organizations",
                "price_monthly": 4999,
                "price_yearly": 49999,
                "job_post_limit": 100,
                "resume_download_limit": 500,
                "featured_jobs": True,
                "company_branding": True,
                "analytics": True,
                "priority_support": True,
            },
        ]

        for plan_data in plans:

            plan, created = SubscriptionPlan.objects.update_or_create(
                slug=plan_data["slug"],
                defaults=plan_data,
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Created: {plan.name}"))
            else:
                self.stdout.write(self.style.WARNING(f"Updated: {plan.name}"))

        self.stdout.write(
            self.style.SUCCESS("All subscription plans created successfully.")
        )
