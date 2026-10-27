from django.db import models


class Patient(models.Model):
    first_name = models.CharField('نام', max_length=50)
    last_name = models.CharField('نام خانوادگی', max_length=70)
    national_id = models.CharField('کد ملی', max_length=10, unique=True)
    mobile = models.CharField('شماره همراه', max_length=15, blank=True)
    created_at = models.DateTimeField('تاریخ ثبت', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'بیمار'
        verbose_name_plural = 'بیماران'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# Create your models here.
