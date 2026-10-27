from django.db import models

from definitions.models import MedicalService, Practitioner
from patients.models import Patient
from reception.models import Admission


class BeautyVisit(models.Model):
    class VisitType(models.TextChoices):
        BEAUTY = 'beauty', 'زیبایی'
        WELLNESS = 'wellness', 'سلامت و مراقبت'

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, verbose_name='مراجع')
    service = models.ForeignKey(MedicalService, on_delete=models.PROTECT, verbose_name='خدمت')
    practitioner = models.ForeignKey(Practitioner, null=True, blank=True, on_delete=models.PROTECT, verbose_name='انجام‌دهنده')
    visit_type = models.CharField('نوع خدمت', max_length=12, choices=VisitType, default=VisitType.BEAUTY)
    treatment_area = models.CharField('ناحیه / مورد خدمت', max_length=120, blank=True)
    notes = models.TextField('توضیحات', blank=True)
    next_session_date = models.DateField('تاریخ جلسه بعد', null=True, blank=True)
    next_session_time = models.TimeField('ساعت جلسه بعد', null=True, blank=True)
    admission = models.OneToOneField(Admission, null=True, blank=True, on_delete=models.PROTECT, verbose_name='ارجاع صندوق')
    created_at = models.DateTimeField('زمان ثبت', auto_now_add=True)

    class Meta:
        verbose_name = 'ثبت خدمت زیبایی و سلامت'
        verbose_name_plural = 'ثبت‌های زیبایی و سلامت'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.patient} — {self.service}'
