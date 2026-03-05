from django.http import JsonResponse
from functools import wraps
from .models.user import Userprofile


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):

            print("USER: ", request.user.username)
            print("AUTH: ", request.user.is_authenticated)

            if not request.user.is_authenticated:
                return JsonResponse({"error": "Authentication required"}, status=401)

            profile, created = Userprofile.objects.get_or_create(user=request.user)

            print("ROLE:", profile.role)

            if profile.role not in allowed_roles:
                return JsonResponse({"error": "Permission denied"}, status=401)

            return view_func(request, *args, **kwargs)

        return wrapper

    return decorator


def login_is_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"error": "Authentication required"}, status=401)

        return view_func(request, *args, **kwargs)

    return wrapper
