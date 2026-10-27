from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from definitions.models import MedicalService, InsuranceProvider
from definitions.models import Practitioner

class Admission(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'در انتظار پرداخت'
        PAID = 'paid', 'تسویه شده'
        CANCELLED = 'cancelled', 'لغو شده'
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, verbose_name='بیمار')
    service = models.ForeignKey(MedicalService, on_delete=models.PROTECT, verbose_name='خدمت')
    practitioner = models.ForeignKey(Practitioner, null=True, on_delete=models.PROTECT, verbose_name='پزشک یا انجام‌دهنده')
    practitioner_name = models.CharField('پزشک یا انجام‌دهنده', max_length=100, blank=True)
    insurance = models.ForeignKey(InsuranceProvider, null=True, blank=True, on_delete=models.PROTECT, verbose_name='بیمه')
    patient_share = models.DecimalField('مبلغ پرداخت بیمار', max_digits=12, decimal_places=0)
    insurer_share = models.DecimalField('مبلغ سهم بیمه', max_digits=12, decimal_places=0, default=0)
    supplementary_share = models.DecimalField('مبلغ سهم بیمه تکمیلی', max_digits=12, decimal_places=0, default=0)
    tracking_code = models.CharField('کد پیگیری', max_length=20, unique=True)
    status = models.CharField('وضعیت', max_length=12, choices=Status, default=Status.OPEN)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='کاربر ثبت‌کننده')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: ordering = ['-created_at']

    def __str__(self):
        return f'کد {self.tracking_code} | {self.patient} | {self.service} | {self.patient_share} ریال'

# Create your models here.
