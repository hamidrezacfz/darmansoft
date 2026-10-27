from django.conf import settings
from django.shortcuts import redirect, render

from .service import activate, current_license, machine_id


def activation(request):
    if settings.DEMO_EDITION:
        active_license, reason = current_license()
        error = ''
        if request.method == 'POST':
            try:
                active_license = activate(
                    request.POST.get('license_code', ''),
                    required_plan='demo',
                    demo_days=3,
                )
                return redirect('/')
            except ValueError as exc:
                error = str(exc)
        return render(request, 'licensing/activation.html', {
            'machine_id': machine_id(),
            'demo_edition': True,
            'license': active_license,
            'reason': reason,
            'error': error,
            'enforced': settings.LICENSE_ENFORCED,
        })
    active_license, reason = current_license()
    error = ''
    if request.method == 'POST':
        try:
            active_license = activate(request.POST.get('license_code', ''))
            return redirect('/')
        except ValueError as exc:
            error = str(exc)
    return render(request, 'licensing/activation.html', {
        'machine_id': machine_id(),
        'license': active_license,
        'reason': reason,
        'error': error,
        'enforced': settings.LICENSE_ENFORCED,
        'demo_edition': settings.DEMO_EDITION,
    })
