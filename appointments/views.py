from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
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
        practitioner_schedules = WorkSchedule.objects.filter(active=True, weekday=info['appointment_at'].weekday(), practitioner=info['practitioner'])
        department_schedules = WorkSchedule.objects.filter(active=True, weekday=info['appointment_at'].weekday(), department=department)
        schedules = practitioner_schedules if practitioner_schedules.exists() else department_schedules
        if schedules.exists() and not schedules.filter(start_time__lte=info['appointment_at'].time(), end_time__gt=info['appointment_at'].time()).exists():
            form.add_error('appointment_time', 'این ساعت خارج از برنامه کاری انتخاب‌شده است.')
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


def work_schedule(request):
    form = WorkScheduleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'برنامه کاری ذخیره شد.')
        return redirect('work_schedule')
    schedules = WorkSchedule.objects.select_related('practitioner', 'department').all()
    return render(request, 'appointments/schedule.html', {'form': form, 'schedules': schedules})


def delete_work_schedule(request, schedule_id):
    if request.method == 'POST':
        get_object_or_404(WorkSchedule, pk=schedule_id).delete()
        messages.success(request, 'بازه برنامه کاری حذف شد.')
    return redirect('work_schedule')
