from functools import wraps
from django.http import HttpResponseForbidden
def role_required(*roles):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.is_superuser: return view(request, *args, **kwargs)
            profile = getattr(request.user, 'userprofile', None)
            if profile and profile.role in roles: return view(request, *args, **kwargs)
            return HttpResponseForbidden('شما اجازهٔ دسترسی به این بخش را ندارید.')
        return wrapped
    return decorator
