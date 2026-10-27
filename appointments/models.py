from django.db import models
from patients.models import Patient
from definitions.models import MedicalService, Practitioner, ServiceCategory


class Appointment(models.Model):
    class Status(models.TextChoices):
        BOOKED = 'booked', 'رزرو شده'
        ARRIVED = 'arrived', 'مراجعه کرده'
        COMPLETED = 'completed', 'اتمام خدمت'
        CANCELLED = 'cancelled', 'لغو شده'

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, verbose_name='بیمار')
    service = models.ForeignKey(MedicalService, null=True, on_delete=models.PROTECT, verbose_name='نوع خدمت')
    practitioner = models.ForeignKey(Practitioner, null=True, blank=True, on_delete=models.PROTECT, verbose_name='پزشک یا انجام‌دهنده')
    appointment_at = models.DateTimeField('تاریخ و ساعت نوبت')
    status = models.CharField('وضعیت', max_length=12, choices=Status, default=Status.BOOKED)
    note = models.CharField('یادداشت', max_length=200, blank=True)
    reminder_requested = models.BooleanField('ارسال یادآوری پیامکی', default=False)
    reminder_status = models.CharField('وضعیت پیامک', max_length=12, choices=[('none', 'درخواست نشده'), ('ready', 'آماده ارسال'), ('sent', 'ارسال شده')], default='none')

    class Meta:
        ordering = ['appointment_at']

    def __str__(self):
        return f'{self.patient} - {self.appointment_at}'

# Create your models here.

class WorkSchedule(models.Model):
    class Weekday(models.IntegerChoices):
        SATURDAY = 5, 'شنبه'
        SUNDAY = 6, 'یکشنبه'
        MONDAY = 0, 'دوشنبه'
        TUESDAY = 1, 'سه‌شنبه'
        WEDNESDAY = 2, 'چهارشنبه'
        THURSDAY = 3, 'پنج‌شنبه'
        FRIDAY = 4, 'جمعه'

    practitioner = models.ForeignKey(Practitioner, null=True, blank=True, on_delete=models.CASCADE, verbose_name='پزشک / انجام‌دهنده')
    department = models.ForeignKey(ServiceCategory, null=True, blank=True, on_delete=models.CASCADE, verbose_name='بخش')
    weekday = models.PositiveSmallIntegerField('روز هفته', choices=Weekday.choices)
    start_time = models.TimeField('شروع کار')
    end_time = models.TimeField('پایان کار')
    active = models.BooleanField('فعال', default=True)

    class Meta:
        ordering = ['weekday', 'start_time']

    def __str__(self):
        target = self.practitioner or self.department
        return f'{target} | {self.get_weekday_display()} {self.start_time}-{self.end_time}'
