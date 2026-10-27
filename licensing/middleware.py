from django.conf import settings
from django.shortcuts import redirect

from .service import current_license


class LicenseRequiredMiddleware:
    """Blocks the packaged product until it has a valid device-bound license."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        allowed = ('/activation/', '/admin/')
        if settings.LICENSE_ENFORCED and not request.path.startswith(allowed):
            if settings.DEMO_EDITION:
                license_data, _ = current_license()
                is_valid_demo = (
                    license_data
                    and license_data.get('plan') == 'demo'
                    and bool(license_data.get('expires_on'))
                )
                if not is_valid_demo:
                    return redirect('activation')
                return self.get_response(request)
            license_data, _ = current_license()
            if not license_data:
                return redirect('activation')
        return self.get_response(request)
