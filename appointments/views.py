from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from patients.models import Patient
from definitions.models import Practitioner
from .forms import AppointmentBookingForm, WorkScheduleForm
from .models import Appointment, WorkSchedule

def patient_lookup(request):
    patient = Patient.objects.filter(national_id=(request.GET.get('national_id') or '').strip()).first()
    return JsonResponse({'found': bool(patient), 'first_name': patient.first_name if patient else '', 'last_name': patient.last_name if patient else '', 'mobile': patient.mobile if patient else ''})

def appointment_list(request):
    form = AppointmentBookingForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        info = form.cleaned_data
        conflict = Appointment.objects.filter(practitioner=info['practitioner'], appointment_at=info['appointment_at']).exclude(status=Appointment.Status.CANCELLED).exists()
        department = info['service'].category
        schedule_filter = Q(schedule_date=info['appointment_at'].date()) | Q(schedule_date__isnull=True, weekday=info['appointment_at'].weekday())
        practitioner_schedules = WorkSchedule.objects.filter(schedule_filter, active=True, practitioner=info['practitioner'])
        department_schedules = WorkSchedule.objects.filter(schedule_filter, active=True, department=department)
        schedules = practitioner_schedules if practitioner_schedules.exists() else department_schedules
        matching = schedules.filter(start_time__lte=info['appointment_at'].time(), end_time__gt=info['appointment_at'].time())
        if schedules.exists() and not matching.exists():
            form.add_error('appointment_time', 'این ساعت خارج از برنامه کاری انتخاب‌شده است.')
        elif matching.exists() and any(Appointment.objects.filter(practitioner=info['practitioner'], appointment_at__date=info['appointment_at'].date(), appointment_at__time__gte=s.start_time, appointment_at__time__lt=s.end_time, status__in=[Appointment.Status.BOOKED, Appointment.Status.ARRIVED]).count() >= s.capacity for s in matching):
            form.add_error('appointment_time', 'ظرفیت این شیفت تکمیل شده است.')
        elif conflict:
            form.add_error('appointment_at', f"برای {info['practitioner']} در این ساعت نوبت دیگری ثبت شده است.")
        else:
            patient, _ = Patient.objects.update_or_create(national_id=info['national_id'], defaults={'first_name':info['first_name'], 'last_name':info['last_name'], 'mobile':info['mobile']})
            Appointment.objects.create(patient=patient, service=info['service'], practitioner=info['practitioner'], appointment_at=info['appointment_at'], note=info['note'], reminder_requested=info['reminder_requested'], reminder_status='ready' if info['reminder_requested'] else 'none')
            messages.success(request, f"نوبت {patient} برای {info['practitioner']} ثبت شد.")
            return redirect('appointment_list')
    selected_date, practitioner_id, national_id = request.GET.get('date','').strip(), request.GET.get('practitioner','').strip(), request.GET.get('national_id','').strip()
    appointments = Appointment.objects.select_related('patient','service','practitioner')
    if selected_date:
        from billing.views import parse_report_date
        parsed = parse_report_date(selected_date)
        if parsed: appointments = appointments.filter(appointment_at__date=parsed)
    if practitioner_id: appointments = appointments.filter(practitioner_id=practitioner_id)
    if national_id: appointments = appointments.filter(patient__national_id=national_id)
    appointments = appointments.order_by('appointment_at')
    from datetime import date
    from core.jalali import ENGLISH_DIGITS, to_jalali
    return render(request, 'appointments/list.html', {'form':form,'appointments':appointments,'practitioners':Practitioner.objects.filter(active=True),'selected':request.GET,'count':appointments.count(),'booked_count':appointments.filter(status=Appointment.Status.BOOKED).count(),'today_jalali':to_jalali(date.today()).translate(ENGLISH_DIGITS)})


def availability(request):
    """Return Jalali-date shift slots and remaining capacity for a practitioner."""
    from datetime import datetime, timedelta
    from core.jalali import from_jalali
    date_value = request.GET.get('date', '').strip()
    practitioner_id = request.GET.get('practitioner', '').strip()
    parsed = parse_jalali_date(date_value)
    if not parsed or not practitioner_id.isdigit(): return JsonResponse({'slots': []})
    schedules = WorkSchedule.objects.filter(Q(schedule_date=parsed) | Q(schedule_date__isnull=True, weekday=parsed.weekday()), active=True, practitioner_id=practitioner_id)
    slots=[]
    for schedule in schedules:
        total_minutes=max(1, int((datetime.combine(parsed,schedule.end_time)-datetime.combine(parsed,schedule.start_time)).total_seconds()//60))
        interval=max(5, total_minutes//max(1,schedule.capacity))
        booked=Appointment.objects.filter(practitioner_id=practitioner_id, appointment_at__date=parsed, status__in=[Appointment.Status.BOOKED,Appointment.Status.ARRIVED])
        for index in range(schedule.capacity):
            current=(datetime.combine(parsed,schedule.start_time)+timedelta(minutes=index*interval)).time()
            if current>=schedule.end_time: break
            used=booked.filter(appointment_at__time=current).exists()
            slots.append({'time':current.strftime('%H:%M'),'label':schedule.shift_name or 'شیفت','available':not used})
    return JsonResponse({'slots':slots})


def parse_jalali_date(value):
    try:
        from core.jalali import from_jalali
        return from_jalali(value)
    except (TypeError, ValueError):
        return None


def work_schedule(request):
    form = WorkScheduleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        data = form.cleaned_data
        if data.get('range_start'):
            from datetime import timedelta
            created = 0; current = data['range_start']; selected = {int(x) for x in data['weekdays']}
            while current <= data['range_end']:
                if current.weekday() in selected:
                    WorkSchedule.objects.create(practitioner=data.get('practitioner'), department=data.get('department'), schedule_date=current, weekday=current.weekday(), start_time=data['start_time'], end_time=data['end_time'], shift_name=data.get('shift_type') or 'شیفت', capacity=data['capacity'], active=data['active'])
                    created += 1
                current += timedelta(days=1)
            messages.success(request, f'برنامهٔ هفتگی برای {created} روز ثبت شد.')
        else:
            form.save(); messages.success(request, 'برنامه کاری ذخیره شد.')
        return redirect('work_schedule')
    schedules = WorkSchedule.objects.select_related('practitioner', 'department').all()
    return render(request, 'appointments/schedule.html', {'form': form, 'schedules': schedules})


def delete_work_schedule(request, schedule_id):
    if request.method == 'POST':
        get_object_or_404(WorkSchedule, pk=schedule_id).delete()
        messages.success(request, 'بازه برنامه کاری حذف شد.')
    return redirect('work_schedule')
