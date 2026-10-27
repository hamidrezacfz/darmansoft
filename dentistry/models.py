from django.db import models
from definitions.models import MedicalService
from reception.models import Admission


class DentalServiceProfile(models.Model):
    service = models.OneToOneField(MedicalService, on_delete=models.CASCADE, related_name='dental_profile')
    tooth_scope = models.CharField('شماره / ناحیه دندان', max_length=100, blank=True)


class DentalAdmissionDetail(models.Model):
    admission = models.OneToOneField(Admission, on_delete=models.CASCADE, related_name='dental_detail')
    tooth_numbers = models.CharField('دندان‌های انتخاب‌شده', max_length=150, blank=True)
    note = models.TextField('توضیحات دندانپزشکی', blank=True)
