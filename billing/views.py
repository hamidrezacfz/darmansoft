from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from .forms import PaymentForm
from .models import Payment
from reception.models import Admission
from django.db.models import Sum
from patients.models import Patient
from definitions.models import InsuranceProvider, MedicalService, Practitioner
from datetime import date


def admission_section(admission):
    """Return the originating clinic section for an admission."""
    category = admission.service.category.name or ''
    service_name = admission.service.name or ''
    if getattr(admission, 'beautyvisit', None):
        return 'زیبایی'
    if category.startswith('دندانپزشکی - '):
        return 'دندان‌پزشکی'
    if any(term in f'{category} {service_name}' for term in ('تصویربرداری', 'ام‌آر‌آی', 'MRI', 'سی‌تی', 'سونوگرافی')):
        return 'تصویربرداری'
    return 'پذیرش'


def referral_preview(request):
    """Return an open referral before it is settled."""
    code = request.GET.get('referral_code', '').strip()
    if not code:
        return JsonResponse({'found': False, 'message': 'کد ارجاع را وارد کنید.'}, status=400)
    try:
        admission = Admission.objects.select_related('patient', 'service__category', 'practitioner').get(
            tracking_code=code, status=Admission.Status.OPEN
        )
    except Admission.DoesNotExist:
        return JsonResponse({'found': False, 'message': 'پذیرش بازی با این کد پیدا نشد یا قبلاً تسویه شده است.'}, status=404)
    return JsonResponse({
        'found': True, 'referral_code': admission.tracking_code,
        'patient': str(admission.patient), 'national_id': admission.patient.national_id,
        'mobile': admission.patient.mobile or '—', 'section': admission_section(admission),
        'service': admission.service.name,
        'practitioner': str(admission.practitioner) if admission.practitioner else '—',
        'amount': str(admission.patient_share),
    })

def parse_report_date(value):
    """Accept Gregorian YYYY-MM-DD or Persian YYYY/MM/DD and return a date."""
    value = (value or '').strip().replace('-', '/')
    if not value:
        return None
    try:
        year, month, day = map(int, value.split('/'))
        if year > 1700:
            return date(year, month, day)
        # Jalali to Gregorian conversion, without an external dependency.
        jy = year + 1595
        days = -355668 + (365 * jy) + (jy // 33 * 8) + (((jy % 33) + 3) // 4) + day
        days += (month - 1) * 31 if month < 7 else ((month - 7) * 30 + 186)
        gy = 400 * (days // 146097); days %= 146097
        if days > 36524:
            gy += 100 * ((days - 1) // 36524); days = (days - 1) % 36524
            if days >= 365: days += 1
        gy += 4 * (days // 1461); days %= 1461
        if days > 365:
            gy += (days - 1) // 365; days = (days - 1) % 365
        gd = days + 1
        leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
        months = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        gm = 1
        for length in months:
            if gd <= length: break
            gd -= length; gm += 1
        return date(gy, gm, gd)
    except (ValueError, TypeError):
        return None

def report(request):
    payments = Payment.objects.select_related('patient', 'admission__insurance', 'admission__service', 'admission__practitioner')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    section = request.GET.get('section', '')
    method = request.GET.get('method', '')
    insurance_id = request.GET.get('insurance', '')
    practitioner_id = request.GET.get('practitioner', '')
    parsed_from, parsed_to = parse_report_date(date_from), parse_report_date(date_to)
    if parsed_from: payments = payments.filter(created_at__date__gte=parsed_from)
    if parsed_to: payments = payments.filter(created_at__date__lte=parsed_to)
    if section == 'dentistry': payments = payments.filter(admission__service__category__name__startswith='دندانپزشکی - ')
    elif section == 'beauty': payments = payments.filter(admission__beautyvisit__isnull=False)
    elif section == 'reception': payments = payments.exclude(admission__service__category__name__startswith='دندانپزشکی - ').filter(admission__beautyvisit__isnull=True)
    if method: payments = payments.filter(method=method)
    if insurance_id: payments = payments.filter(admission__insurance_id=insurance_id)
    if practitioner_id: payments = payments.filter(admission__practitioner_id=practitioner_id)
    total = payments.aggregate(value=Sum('amount'))['value'] or 0
    return render(request, 'billing/report.html', {'payments': payments, 'total': total, 'count': payments.count(), 'sections': [('reception', 'پذیرش'), ('beauty', 'زیبایی'), ('dentistry', 'دندان‌پزشکی')], 'methods': Payment.Method.choices, 'insurances': InsuranceProvider.objects.filter(active=True), 'services': MedicalService.objects.filter(active=True), 'practitioners': Practitioner.objects.filter(active=True), 'selected': request.GET})
def payment_list(request):
    form = PaymentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        admission = form.admission
        payment = Payment.objects.create(patient=admission.patient, admission=admission, amount=admission.patient_share, method=form.cleaned_data['method'], note=form.cleaned_data['note'])
        admission.status = Admission.Status.PAID
        admission.save(update_fields=['status'])
        return redirect('payment_receipt', payment_id=payment.id)
    from django.utils import timezone
    today = timezone.localdate()
    today_payments = Payment.objects.filter(created_at__date=today)
    method_totals = {method: today_payments.filter(method=method).aggregate(value=Sum('amount'))['value'] or 0 for method, _ in Payment.Method.choices}
    pending = Admission.objects.filter(status=Admission.Status.OPEN).select_related(
        'patient', 'service__category', 'practitioner', 'beautyvisit'
    ).order_by('created_at')
    pending_rows = [{'admission': admission, 'section': admission_section(admission)} for admission in pending]
    return render(request, 'billing/list.html', {
        'form': form, 'pending_rows': pending_rows, 'method_choices': Payment.Method.choices,
        'method_totals': method_totals, 'pending_count': len(pending_rows),
    })
def payment_receipt(request, payment_id):
    payment = get_object_or_404(Payment.objects.select_related('patient', 'admission__service', 'admission__insurance'), pk=payment_id)
    return render(request, 'billing/receipt.html', {'payment': payment})

# Create your views here.
