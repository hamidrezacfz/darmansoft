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

    @property
    def tooth_labels(self):
        quadrants = {'1': 'بالا راست', '2': 'بالا چپ', '3': 'پایین چپ', '4': 'پایین راست'}
        parts = self.tooth_numbers.replace(',', '،').split('،')
        return '، '.join(f'{p.strip()[1]} {quadrants[p.strip()[0]]}' if len(p.strip()) == 2 and p.strip()[0] in quadrants and p.strip()[1] in '12345678' else p.strip() for p in parts if p.strip())
