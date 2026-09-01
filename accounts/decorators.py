from functools import wraps
from django.shortcuts import redirect


def role_required(role):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Safe check to handle unauthenticated users or missing role attribute
            user_role = getattr(request.user, "role", None)

            if user_role != role:
                return redirect("accounts:dashboard")

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator
