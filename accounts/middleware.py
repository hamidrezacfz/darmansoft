from django.shortcuts import redirect
from django.conf import settings
class LoginRequiredMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        allowed = (settings.LOGIN_URL, '/logout/', '/activation/', '/admin/')
        if not request.user.is_authenticated and not request.path.startswith(allowed):
            return redirect(settings.LOGIN_URL)
        return self.get_response(request)
