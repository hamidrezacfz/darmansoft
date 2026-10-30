from django.http import JsonResponse
from django.shortcuts import redirect, render

from definitions.models import InsuranceTariff
from patients.models import Patient
from reception.models import Admission

from .forms import ImagingAdmissionForm


def patient_lookup(request):
    patient = Patient.objects.filter(national_id=request.GET.get('national_id', '').strip()).first()
    return JsonResponse({'found': bool(patient), 'first_name': patient.first_name if patient else '', 'last_name': patient.last_name if patient else '', 'mobile': patient.mobile if patient else ''})


def tariff_preview(request):
    service_id = request.GET.get('service')
    service = ImagingAdmissionForm().fields['service'].queryset.filter(pk=service_id).first()
    if not service:
        return JsonResponse({'found': False})
    patient_share, insurer_share = service.base_price, 0
    insurance_id = request.GET.get('insurance')
    if insurance_id:
        tariff = InsuranceTariff.objects.filter(service=service, insurance_id=insurance_id).first()
        if tariff:
            tariff.apply_calculation()
            patient_share, insurer_share = tariff.patient_share, tariff.insurer_share
    return JsonResponse({'found': True, 'patient_share': str(patient_share), 'insurer_share': str(insurer_share)})


def index(request):
    form = ImagingAdmissionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        patient, _ = Patient.objects.update_or_create(
            national_id=data['national_id'],
            defaults={'first_name': data['first_name'], 'last_name': data['last_name'], 'mobile': data['mobile']},
        )
        last = Admission.objects.order_by('-id').first()
        next_code = int(last.tracking_code) + 1 if last and last.tracking_code.isdigit() else 100
        admission = Admission.objects.create(
            patient=patient, service=data['service'], practitioner=data['practitioner'], insurance=data['insurance'],
            patient_share=data['patient_share'], insurer_share=data['insurer_share'] or 0, supplementary_share=0,
            tracking_code=str(next_code), created_by=request.user if request.user.is_authenticated else None,
        )
        return redirect(f'/imaging/?ref={admission.tracking_code}')
    return render(request, 'imaging/index.html', {'form': form, 'referral_code': request.GET.get('ref', '')})
