from django.shortcuts import redirect, render

from patients.models import Patient

from .forms import BeautyVisitForm
from .models import BeautyVisit
from reception.models import Admission


def index(request):
    form = BeautyVisitForm(request.POST or None)
    query = request.GET.get('q', '').strip()
    visits = BeautyVisit.objects.select_related('patient', 'service', 'practitioner')
    if query:
        visits = visits.filter(patient__national_id__icontains=query) | visits.filter(patient__first_name__icontains=query) | visits.filter(patient__last_name__icontains=query)
    else:
        visits = visits[:30]

    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        patient, created = Patient.objects.get_or_create(
            national_id=data['national_id'],
            defaults={'first_name': data['first_name'], 'last_name': data['last_name'], 'mobile': data['mobile']},
        )
        if not created:
            changed = []
            for field in ('first_name', 'last_name', 'mobile'):
                if data[field] and getattr(patient, field) != data[field]:
                    setattr(patient, field, data[field])
                    changed.append(field)
            if changed:
                patient.save(update_fields=changed)
        last_admission = Admission.objects.order_by('-id').first()
        next_code = int(last_admission.tracking_code) + 1 if last_admission and last_admission.tracking_code.isdigit() else 100
        admission = Admission.objects.create(
            patient=patient, service=data['service'], practitioner=data['practitioner'],
            patient_share=data['service'].base_price, insurer_share=0, supplementary_share=0,
            tracking_code=str(next_code), created_by=request.user if request.user.is_authenticated else None,
        )
        BeautyVisit.objects.create(
            patient=patient,
            service=data['service'],
            practitioner=data['practitioner'],
            visit_type=data['visit_type'],
            treatment_area=data['treatment_area'],
            notes=data['notes'],
            next_session_date=data['next_session_date'],
            next_session_time=data['next_session_time'],
            admission=admission,
        )
        return redirect(f'/beauty/?ref={admission.tracking_code}')

    from datetime import date
    from core.jalali import ENGLISH_DIGITS, to_jalali
    return render(request, 'aesthetics/index.html', {'form': form, 'query': query, 'referral_code': request.GET.get('ref', ''), 'today_jalali': to_jalali(date.today()).translate(ENGLISH_DIGITS)})
