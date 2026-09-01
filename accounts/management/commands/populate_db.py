from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

# Saare models ke imports ek jagah (Top par)
from accounts.models import (
    JobCategory,
    Industry,
    Skill,
    Company,
    Job,
    JobSeekerProfile,
    Resume,
    Application,
)
from cms.models import BlogPost, FAQ, Testimonial, StaticPage
from ads.models import AdCampaign, Advertisement
from billing.models import (
    SubscriptionPlan,
    Subscription,
    SubscriptionUsage,
    PaymentHistory,
    Invoice,
    Coupon,
)
from support.models import TicketCategory, SupportTicket, TicketReply

User = get_user_model()


class Command(BaseCommand):
    help = "Populates the database with comprehensive dummy data for all modules."

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting comprehensive database population...")

        # 1. Create Sample Users
        admin_user, _ = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@smartjobs.com",
                "is_staff": True,
                "is_superuser": True,
                "role": "ADMIN",
            },
        )
        admin_user.set_password("admin123")
        admin_user.save()

        employer_user, _ = User.objects.get_or_create(
            username="employer_tcs",
            defaults={
                "email": "hr@tcs.com",
                "role": "EMPLOYER",
                "first_name": "TCS",
                "last_name": "HR",
            },
        )
        employer_user.set_password("password123")
        employer_user.save()

        seeker_user, _ = User.objects.get_or_create(
            username="aman_seeker",
            defaults={
                "email": "aman@gmail.com",
                "role": "JOB_SEEKER",
                "first_name": "Aman",
                "last_name": "Kumar",
            },
        )
        seeker_user.set_password("password123")
        seeker_user.save()

        # 2. Categories & Industries
        categories = ["Software Development", "Data Science", "Marketing", "Design"]
        cat_objs = []
        for cat in categories:
            obj, _ = JobCategory.objects.update_or_create(
                slug=cat.lower().replace(" ", "-"),
                defaults={"name": cat, "is_active": True},
            )
            cat_objs.append(obj)

        industries = ["Information Technology", "Fintech", "E-commerce"]
        ind_objs = []
        for ind in industries:
            obj, _ = Industry.objects.update_or_create(
                slug=ind.lower().replace(" ", "-"),
                defaults={"name": ind, "is_active": True},
            )
            ind_objs.append(obj)

        # 3. Company
        company, _ = Company.objects.get_or_create(
            name="Tata Consultancy Services",
            defaults={
                "employer": employer_user,
                "description": "Global IT services and consulting organization.",
                "website": "https://www.tcs.com",
                "location": "Mumbai, India",
                "is_verified": True,
            },
        )

        # 4. Job Posting
        job, _ = Job.objects.get_or_create(
            title="Python Developer",
            company=company,
            defaults={
                "description": "Looking for an experienced Python and Django developer with strong backend skills.",
                "category": cat_objs[0],
                "industry": ind_objs[0],
                "location": "Bangalore, India",
                "salary_min": 600000,
                "salary_max": 1200000,
                "experience_min": 2,
                "experience_max": 5,
                "employment_type": "Full-time",
                "work_mode": "Remote",
                "is_active": True,
                "is_approved": True,
                "expires_at": timezone.now() + timedelta(days=30),
            },
        )

        # 5. Job Seeker Profile & Resume
        profile, _ = JobSeekerProfile.objects.get_or_create(
            user=seeker_user,
            defaults={
                "phone": "9876543210",
                "gender": "Male",
                "location": "Delhi, India",
                "bio": "Passionate Python and Django developer ready to build scalable web applications.",
            },
        )

        resume, _ = Resume.objects.get_or_create(
            profile=profile, title="Aman_Resume.pdf", defaults={"is_default": True}
        )

        # 6. Job Application
        Application.objects.get_or_create(
            job=job,
            applicant=seeker_user,
            defaults={
                "resume": resume,
                "cover_letter": "I am very excited to apply for this Python Developer position at TCS.",
                "status": "Pending",
            },
        )

        # 7. CMS (FAQs & Testimonials)
        FAQ.objects.get_or_create(
            question="How do I apply for a job?",
            defaults={
                "answer": "Go to the job listing, click view details, and click the Apply button.",
                "category": "General",
                "is_active": True,
            },
        )
        FAQ.objects.get_or_create(
            question="How do I reset my password?",
            defaults={
                "answer": "Click on 'Forgot Password' on the login page.",
                "category": "Support",
                "is_active": True,
            },
        )
        Testimonial.objects.get_or_create(
            name="Aman Kumar",
            defaults={
                "role_or_company": "Software Engineer",
                "content": "SmartJobs made finding a job incredibly easy!",
                "rating": 5,
                "is_featured": True,
            },
        )

        # 8. Ads App Data
        campaign, _ = AdCampaign.objects.get_or_create(
            title="Summer Hiring Drive 2026",
            defaults={
                "advertiser": employer_user,
                "budget": 50000.00,
                "spent": 12000.50,
                "start_date": timezone.now().date(),
                "end_date": timezone.now().date() + timedelta(days=30),
                "target_location": "India",
                "target_industry": "Information Technology",
                "status": "Active",
            },
        )
        Advertisement.objects.get_or_create(
            title="Featured TCS Developer Jobs",
            defaults={
                "campaign": campaign,
                "ad_type": "Banner",
                "destination_url": "/jobs/python-developer/",
                "is_active": True,
                "impressions": 1500,
                "clicks": 120,
                "cpc": 2.50,
            },
        )

        # 9. Billing App Data
        free_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Free Plan",
            defaults={
                "price": 0.00,
                "job_post_limit": 1,
                "resume_download_limit": 5,
                "is_active": True,
            },
        )
        pro_plan, _ = SubscriptionPlan.objects.get_or_create(
            name="Pro Growth Plan",
            defaults={
                "price": 4999.00,
                "job_post_limit": 10,
                "resume_download_limit": 100,
                "can_feature_jobs": True,
                "is_active": True,
            },
        )
        Coupon.objects.get_or_create(
            code="WELCOME20",
            defaults={
                "discount_percent": 20,
                "valid_from": timezone.now(),
                "valid_to": timezone.now() + timedelta(days=60),
                "active": True,
                "max_uses": 100,
            },
        )
        sub, _ = Subscription.objects.get_or_create(
            user=employer_user,
            defaults={
                "plan": pro_plan,
                "status": "ACTIVE",
                "start_date": timezone.now(),
                "end_date": timezone.now() + timedelta(days=30),
            },
        )
        SubscriptionUsage.objects.get_or_create(
            subscription=sub, defaults={"jobs_posted": 1, "resumes_downloaded": 3}
        )
        payment, _ = PaymentHistory.objects.get_or_create(
            razorpay_order_id="order_N987654321",
            defaults={
                "user": employer_user,
                "plan": pro_plan,
                "amount": 4999.00,
                "status": "SUCCESS",
            },
        )
        Invoice.objects.get_or_create(
            invoice_number="INV-2026-0001",
            defaults={
                "payment": payment,
                "user": employer_user,
                "base_amount": 4236.44,
                "gst_amount": 762.56,
                "total_amount": 4999.00,
            },
        )

        # 10. CMS Extra (Blog & Static Pages)
        BlogPost.objects.get_or_create(
            slug="top-5-python-interview-questions",
            defaults={
                "meta_title": "Top 5 Python Interview Questions",
                "title": "Top 5 Python Interview Questions in 2026",
                "author": "Admin",
                "content": "Python content here...",
                "is_published": True,
            },
        )
        StaticPage.objects.get_or_create(
            slug="about-us",
            defaults={
                "meta_title": "About Us",
                "title": "About Us",
                "content": "Welcome to SmartJobs!",
                "is_indexable": True,
            },
        )

        # 11. Support App Data
        ticket_cat, _ = TicketCategory.objects.get_or_create(
            name="Technical Issues",
            defaults={
                "description": "Issues related to website errors, login, or dashboard bugs."
            },
        )
        ticket, _ = SupportTicket.objects.get_or_create(
            ticket_id="TKT-2026-0001",
            defaults={
                "user": seeker_user,
                "category": ticket_cat,
                "subject": "Unable to upload resume",
                "description": "I am trying to upload my PDF resume but getting an error message.",
                "priority": "High",
                "status": "Open",
            },
        )
        TicketReply.objects.get_or_create(
            ticket=ticket,
            user=admin_user,
            defaults={
                "message": "Hi Aman, could you please try clearing your browser cache and uploading again? If it still fails, let us know the file size."
            },
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully populated ALL modules and models without any errors!"
            )
        )
