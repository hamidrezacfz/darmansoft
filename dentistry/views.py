from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import redirect, render
from definitions.models import InsuranceTariff, MedicalService, Practitioner, ServiceCategory
from .forms import DentalAdmissionForm, DentalServiceForm, DentalTariffForm, GroupPriceForm
from .models import DentalAdmissionDetail, DentalServiceProfile

PREFIX = 'دندانپزشکی - '

def index(request):
    groups = ServiceCategory.objects.filter(name__startswith=PREFIX).order_by('name')
    services = MedicalService.objects.filter(category__in=groups).select_related('category', 'dental_profile').order_by('category__name', 'name')
    service_form = DentalServiceForm(request.POST or None, prefix='service', groups=groups)
    group_price_form = GroupPriceForm(request.POST or None, prefix='group_price', groups=groups)
    tariff_form = DentalTariffForm(request.POST or None, prefix='tariff', services=services)
    form_name = request.POST.get('form_name')
    if request.method == 'POST' and form_name == 'service' and service_form.is_valid():
        data = service_form.cleaned_data
        item = MedicalService.objects.create(category=data['group'], code=data['code'], standard_code=data['standard_code'] or None, name=data['name'], base_price=data['base_price'])
        DentalServiceProfile.objects.create(service=item, tooth_scope=data['tooth_scope'])
        return redirect('dentistry')
    if request.method == 'POST' and form_name == 'group_price' and group_price_form.is_valid():
        data = group_price_form.cleaned_data
        MedicalService.objects.filter(category=data['group']).update(base_price=data['base_price'])
        return redirect('dentistry')
    if request.method == 'POST' and form_name == 'tariff' and tariff_form.is_valid():
        data = tariff_form.cleaned_data
        InsuranceTariff.objects.update_or_create(service=data['service'], insurance=data['insurance'], defaults={'patient_share': data['patient_share'], 'insurer_share': data['insurer_share'], 'supplementary_share': data['supplementary_share']})
        return redirect('dentistry')
    tariffs = InsuranceTariff.objects.filter(service__category__in=groups).select_related('service', 'insurance').order_by('service__category__name', 'service__name', 'insurance__name')
    return render(request, 'dentistry/index.html', {'service_form': service_form, 'group_price_form': group_price_form, 'tariff_form': tariff_form, 'services': services, 'tariffs': tariffs, 'groups': groups})


def admission(request):
    groups = ServiceCategory.objects.filter(name__startswith=PREFIX)
    services = MedicalService.objects.filter(category__in=groups, active=True).order_by('category__name', 'name')
    form = DentalAdmissionForm(request.POST or None, services=services)
    if request.method == 'POST' and form.is_valid():
        from patients.models import Patient
        from reception.models import Admission
        data = form.cleaned_data
        patient, created = Patient.objects.get_or_create(national_id=data['national_id'], defaults={'first_name': data['first_name'], 'last_name': data['last_name'], 'mobile': data['mobile']})
        if not created:
            changed = []
            for field in ('first_name', 'last_name', 'mobile'):
                if data[field] and getattr(patient, field) != data[field]:
                    setattr(patient, field, data[field]); changed.append(field)
            if changed: patient.save(update_fields=changed)
        last = Admission.objects.order_by('-id').first()
        code = str(int(last.tracking_code) + 1) if last and last.tracking_code.isdigit() else '100'
        admission_record = Admission.objects.create(patient=patient, service=data['service'], practitioner=data['practitioner'], practitioner_name=(str(data['practitioner']) if data['practitioner'] else ''), patient_share=data['service'].base_price, insurer_share=0, supplementary_share=0, tracking_code=code, created_by=request.user if request.user.is_authenticated else None)
        DentalAdmissionDetail.objects.create(admission=admission_record, tooth_numbers=data['tooth_numbers'], note=data['note'])
        return redirect(f'/dentistry/admission/?ref={code}')
    return render(request, 'dentistry/admission.html', {'form': form, 'referral_code': request.GET.get('ref', '')})


def report(request):
    from django.db.models import Sum
    from reception.models import Admission
    groups = ServiceCategory.objects.filter(name__startswith=PREFIX)
    rows = Admission.objects.filter(service__category__in=groups).select_related('patient', 'service', 'practitioner').order_by('-created_at')
    query = request.GET.get('q', '').strip()
    practitioner_id = request.GET.get('practitioner', '').strip()
    group_id = request.GET.get('group', '').strip()
    service_id = request.GET.get('service', '').strip()
    status = request.GET.get('status', '').strip()
    date_from = request.GET.get('date_from', '').strip()
    date_to = request.GET.get('date_to', '').strip()
    if query:
        rows = rows.filter(Q(patient__national_id__icontains=query) | Q(patient__first_name__icontains=query) | Q(patient__last_name__icontains=query) | Q(service__name__icontains=query))
    if practitioner_id.isdigit(): rows = rows.filter(practitioner_id=practitioner_id)
    if group_id.isdigit(): rows = rows.filter(service__category_id=group_id)
    if service_id.isdigit(): rows = rows.filter(service_id=service_id)
    if status in Admission.Status.values: rows = rows.filter(status=status)
    if date_from: rows = rows.filter(created_at__date__gte=date_from)
    if date_to: rows = rows.filter(created_at__date__lte=date_to)
    stats = rows.aggregate(count=Count('id'), total=Sum('patient_share'), average=Avg('patient_share'), paid_count=Count('id', filter=Q(status=Admission.Status.PAID)))
    return render(request, 'dentistry/report.html', {'rows': rows[:200], 'query': query, 'practitioners': Practitioner.objects.filter(active=True).order_by('name'), 'groups': groups, 'services': MedicalService.objects.filter(category__in=groups, active=True).order_by('category__name', 'name'), 'status_choices': Admission.Status.choices, 'filters': {'practitioner': practitioner_id, 'group': group_id, 'service': service_id, 'status': status, 'date_from': date_from, 'date_to': date_to}, 'count': stats['count'] or 0, 'total': stats['total'] or 0, 'average': stats['average'] or 0, 'paid_count': stats['paid_count'] or 0})
