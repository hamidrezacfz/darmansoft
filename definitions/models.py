from django.db import models

class ServiceCategory(models.Model):
    name = models.CharField('نام دسته', max_length=80, unique=True)
    def __str__(self): return self.name

class PractitionerGroup(models.Model):
    name = models.CharField('نام گروه', max_length=80, unique=True)
    active = models.BooleanField('فعال', default=True)
    class Meta: verbose_name = 'گروه پرسنل'; verbose_name_plural = 'گروه‌های پرسنل'
    def __str__(self): return self.name

class Practitioner(models.Model):
    name = models.CharField('نام پزشک یا انجام‌دهنده', max_length=100)
    medical_system_code = models.CharField('کد نظام پزشکی / پرسنلی', max_length=30, null=True, blank=True, unique=True)
    group = models.ForeignKey(PractitionerGroup, null=True, blank=True, on_delete=models.PROTECT, verbose_name='گروه شغلی')
    role = models.CharField('سمت / تخصص', max_length=100, blank=True)
    share_percent = models.DecimalField('درصد سهم از عملکرد', max_digits=5, decimal_places=2, default=0)
    active = models.BooleanField('فعال', default=True)
    def __str__(self): return f'{self.name} — {self.role}' if self.role else self.name

class MedicalService(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.PROTECT, verbose_name='دسته‌بندی')
    code = models.CharField('کد انحصاری خدمت', max_length=20, unique=True, null=True, blank=True)
    standard_code = models.CharField('کد استاندارد خدمت', max_length=30, unique=True, null=True, blank=True)
    name = models.CharField('نام خدمت', max_length=120)
    base_price = models.DecimalField('تعرفه آزاد (ریال)', max_digits=12, decimal_places=0)
    active = models.BooleanField('فعال', default=True)
    def __str__(self): return f'{self.code or "بدون کد"} — {self.name}'

class InsuranceProvider(models.Model):
    organization = models.CharField('سازمان بیمه‌گر', max_length=100)
    name = models.CharField('نام بیمه', max_length=100)
    active = models.BooleanField('فعال', default=True)
    class Meta: unique_together = [('organization', 'name')]
    def __str__(self): return f'{self.organization} — {self.name}'

class InsuranceTariff(models.Model):
    service = models.ForeignKey(MedicalService, on_delete=models.CASCADE, verbose_name='خدمت')
    insurance = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, verbose_name='بیمه')
    patient_share = models.DecimalField('سهم بیمار (ریال)', max_digits=12, decimal_places=0)
    insurer_share = models.DecimalField('سهم بیمه (ریال)', max_digits=12, decimal_places=0)
    supplementary_share = models.DecimalField('سهم بیمه تکمیلی (ریال)', max_digits=12, decimal_places=0, default=0)
    class Meta: unique_together = [('service', 'insurance')]

    def __str__(self):
        return f'{self.service.name} — {self.insurance.name}'

# Create your models here.
