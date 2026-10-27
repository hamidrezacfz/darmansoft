from django.db import models
from patients.models import Patient
from reception.models import Admission


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = 'cash', 'نقدی'
        CARD = 'card', 'کارت‌خوان'
        TRANSFER = 'transfer', 'واریز'

    patient = models.ForeignKey(Patient, on_delete=models.PROTECT, verbose_name='بیمار')
    admission = models.OneToOneField(Admission, null=True, blank=True, on_delete=models.PROTECT, verbose_name='پذیرش')
    amount = models.DecimalField('مبلغ (ریال)', max_digits=12, decimal_places=0)
    method = models.CharField('روش پرداخت', max_length=10, choices=Method, default=Method.CASH)
    note = models.CharField('شرح', max_length=200, blank=True)
    created_at = models.DateTimeField('زمان ثبت', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

# Create your models here.
