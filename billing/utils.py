from billing.models import Subscription, SubscriptionUsage


def check_user_limit(user, limit_type):
    """
    limit_type: 'job_post' or 'resume_download'
    Returns: (can_perform: bool, message: str)
    """
    subscription = Subscription.objects.filter(user=user, status="active").first()

    if not subscription:
        return False, "Aapke paas koi active subscription plan nahi hai."

    usage, _ = SubscriptionUsage.objects.get_or_create(subscription=subscription)
    plan = subscription.plan

    if limit_type == "job_post":
        # -1 matlab unlimited
        if plan.job_posting_limit != -1 and usage.jobs_posted >= plan.job_posting_limit:
            return (
                False,
                f"Aapki job posting limit ({plan.job_posting_limit}) khatam ho gayi hai.",
            )
        return True, ""

    elif limit_type == "resume_download":
        if (
            plan.resume_download_limit != -1
            and usage.resumes_downloaded >= plan.resume_download_limit
        ):
            return (
                False,
                f"Aapki resume download limit ({plan.resume_download_limit}) khatam ho gayi hai.",
            )
        return True, ""

    return False, "Invalid action."
