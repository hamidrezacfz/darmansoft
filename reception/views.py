from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .models import Admission
from .forms import AdmissionForm, OpenAdmissionEditForm
from patients.models import Patient
from definitions.models import MedicalService
from definitions.models import InsuranceTariff
from definitions.models import Practitioner

def tariff_preview(request):
    code = request.GET.get('service_code', '').strip()
    insurance_id = request.GET.get('insurance', '')
    try:
        service = MedicalService.objects.get(code=code, active=True)
        if service.category.name.startswith('دندانپزشکی - '):
            raise MedicalService.DoesNotExist
    except MedicalService.DoesNotExist:
        service = MedicalService.objects.filter(name__iexact=code, active=True).exclude(category__name__startswith='دندانپزشکی - ').first()
        if not service:
            return JsonResponse({'found': False})
    patient_share, insurer_share, supplementary_share = service.base_price, 0, 0
    if insurance_id:
        tariff = InsuranceTariff.objects.filter(service=service, insurance_id=insurance_id).first()
        if tariff:
            patient_share, insurer_share, supplementary_share = tariff.patient_share, tariff.insurer_share, tariff.supplementary_share
    return JsonResponse({'found': True, 'service': service.name, 'base_price': str(service.base_price), 'patient_share': str(patient_share), 'insurer_share': str(insurer_share), 'supplementary_share': str(supplementary_share)})

def service_lookup(request):
    query = request.GET.get('q', '').strip()
    if len(query) < 2:
        return JsonResponse({'items': []})
    services = (MedicalService.objects.filter(active=True, code__icontains=query) | MedicalService.objects.filter(active=True, name__icontains=query)).exclude(category__name__startswith='دندانپزشکی - ').distinct()[:8]
    # Older services may not have an internal code. In that case the service
    # name is safely used as the selectable value.
    return JsonResponse({'items': [{'code': x.code or x.name, 'name': x.name, 'price': str(x.base_price)} for x in services]})

def patient_lookup(request):
    national_id = request.GET.get('national_id', '').strip()
    patient = Patient.objects.filter(national_id=national_id).first()
    if not patient:
        return JsonResponse({'found': False})
    return JsonResponse({'found': True, 'id': patient.id, 'first_name': patient.first_name, 'last_name': patient.last_name, 'mobile': patient.mobile})

def practitioner_lookup(request):
    code = request.GET.get('code', '').strip()
    person = Practitioner.objects.filter(medical_system_code=code, active=True).first()
    if not person:
        return JsonResponse({'found': False})
    return JsonResponse({'found': True, 'id': person.id, 'name': person.name, 'role': person.role})

def edit_open_admission(request, tracking_code):
    admission = get_object_or_404(Admission.objects.select_related('patient'), tracking_code=tracking_code)
    if admission.status != Admission.Status.OPEN:
        return render(request, 'reception/edit_locked.html', {'admission': admission}, status=403)
    initial = {'first_name': admission.patient.first_name, 'last_name': admission.patient.last_name,
               'mobile': admission.patient.mobile, 'service': admission.service, 'practitioner': admission.practitioner,
               'insurance': admission.insurance, 'patient_share': admission.patient_share,
               'insurer_share': admission.insurer_share, 'supplementary_share': admission.supplementary_share}
    form = OpenAdmissionEditForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        if request.POST.get('confirmed') != '1':
            return render(request, 'reception/confirm.html', {'form': form})
        data = form.cleaned_data
        patient = admission.patient
        patient.first_name, patient.last_name, patient.mobile = data['first_name'], data['last_name'], data['mobile']
        patient.save(update_fields=['first_name', 'last_name', 'mobile'])
        admission.service, admission.practitioner, admission.insurance = data['service'], data['practitioner'], data['insurance']
        admission.patient_share, admission.insurer_share, admission.supplementary_share = data['patient_share'], data['insurer_share'] or 0, data['supplementary_share'] or 0
        admission.practitioner_name = str(admission.practitioner) if admission.practitioner else ''
        admission.save()
        return redirect(f'/reception/edit/{admission.tracking_code}/?saved=1')
    return render(request, 'reception/edit.html', {'form': form, 'admission': admission, 'saved': request.GET.get('saved')})

def index(request):
    form = AdmissionForm(request.POST or None)
    query = request.GET.get('q', '').strip()
    admissions = None
    if query:
        all_admissions = Admission.objects.select_related('patient', 'service', 'insurance', 'practitioner')
        admissions = all_admissions.filter(patient__national_id__icontains=query) | all_admissions.filter(patient__first_name__icontains=query) | all_admissions.filter(patient__last_name__icontains=query) | all_admissions.filter(tracking_code__icontains=query)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        try:
            service = MedicalService.objects.get(code=data['service_code'], active=True)
            if service.category.name.startswith('دندانپزشکی - '): raise MedicalService.DoesNotExist
        except MedicalService.DoesNotExist:
            service = MedicalService.objects.filter(name__iexact=data['service_code'], active=True).exclude(category__name__startswith='دندانپزشکی - ').first()
            if not service:
                form.add_error('service_code', 'خدمتی با این کد یا نام پیدا نشد.')
                return render(request, 'reception/index.html', {'form': form, 'admissions': admissions, 'query': query})
        patient, created = Patient.objects.get_or_create(
            national_id=data['national_id'],
            defaults={'first_name': data['first_name'], 'last_name': data['last_name'], 'mobile': data['mobile']},
        )
        if not created and data['mobile']:
            patient.mobile = data['mobile']; patient.save(update_fields=['mobile'])
        last_admission = Admission.objects.order_by('-id').first()
        next_code = 100
        if last_admission and last_admission.tracking_code.isdigit():
            next_code = int(last_admission.tracking_code) + 1
        admission = Admission(
            patient=patient, service=service, practitioner=data['practitioner'], insurance=data['insurance'],
            patient_share=data['patient_share'], insurer_share=data['insurer_share'] or 0, supplementary_share=data['supplementary_share'] or 0,
            tracking_code=str(next_code),
        )
        if request.user.is_authenticated: admission.created_by = request.user
        admission.save(); return redirect(f'/reception/edit/{admission.tracking_code}/?created=1')
    return render(request, 'reception/index.html', {'form': form, 'admissions': admissions[:50] if admissions is not None else None, 'query': query, 'referral_code': request.GET.get('ref', '')})

# Create your views here.
