from decimal import Decimal, ROUND_HALF_UP
from django.db import models

class ServiceCategory(models.Model):
    class Panel(models.TextChoices):
        GENERAL = 'general', 'پذیرش عمومی'
        DENTISTRY = 'dentistry', 'دندان‌پزشکی'
        IMAGING = 'imaging', 'تصویربرداری'
        AESTHETICS = 'aesthetics', 'زیبایی و سلامت'

    code = models.CharField('کد دسته', max_length=20, unique=True)
    name = models.CharField('نام دسته', max_length=80, unique=True)
    panel = models.CharField('پنل مربوطه', max_length=20, choices=Panel.choices, default=Panel.GENERAL)
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
    base_price = models.DecimalField('تعرفه آزاد (ریال)', max_digits=12, decimal_places=0, default=0)
    technical_k = models.DecimalField('K فنی', max_digits=12, decimal_places=4, default=0)
    professional_k = models.DecimalField('K حرفه‌ای', max_digits=12, decimal_places=4, default=0)
    active = models.BooleanField('فعال', default=True)
    def __str__(self): return f'{self.code or "بدون کد"} — {self.name}'

class InsuranceProvider(models.Model):
    organization = models.CharField('سازمان بیمه‌گر', max_length=100)
    name = models.CharField('نام بیمه', max_length=100)
    active = models.BooleanField('فعال', default=True)
    class Meta: unique_together = [('organization', 'name')]
    def __str__(self): return f'{self.organization} — {self.name}'

class InsuranceTariff(models.Model):
    class PricingMethod(models.TextChoices):
        FIXED = 'fixed', 'مبلغ ثابت'
        K_BASED = 'k_based', 'محاسبه بر اساس K'

    class ShareMode(models.TextChoices):
        AMOUNT = 'amount', 'مبلغ ریالی'
        PERCENT = 'percent', 'درصد از مبلغ کل'

    service = models.ForeignKey(MedicalService, on_delete=models.CASCADE, verbose_name='خدمت')
    insurance = models.ForeignKey(InsuranceProvider, on_delete=models.CASCADE, verbose_name='بیمه')
    pricing_method = models.CharField('روش محاسبه تعرفه', max_length=12, choices=PricingMethod.choices, default=PricingMethod.FIXED)
    fixed_total = models.DecimalField('مبلغ کل تعرفه (ریال)', max_digits=14, decimal_places=0, default=0)
    technical_k_coefficient = models.DecimalField('ضریب K فنی (ریال)', max_digits=14, decimal_places=0, default=0)
    professional_k_coefficient = models.DecimalField('ضریب K حرفه‌ای (ریال)', max_digits=14, decimal_places=0, default=0)
    share_mode = models.CharField('روش ثبت سهم‌ها', max_length=10, choices=ShareMode.choices, default=ShareMode.AMOUNT)
    patient_share = models.DecimalField('سهم بیمار (ریال)', max_digits=12, decimal_places=0)
    insurer_share = models.DecimalField('سهم بیمه (ریال)', max_digits=12, decimal_places=0)
    supplementary_share = models.DecimalField('سهم بیمه تکمیلی (ریال)', max_digits=12, decimal_places=0, default=0)
    difference_share = models.DecimalField('مابه‌التفاوت (ریال)', max_digits=12, decimal_places=0, default=0)
    patient_share_percent = models.DecimalField('درصد سهم بیمار', max_digits=7, decimal_places=3, default=0)
    insurer_share_percent = models.DecimalField('درصد سهم سازمان', max_digits=7, decimal_places=3, default=0)
    supplementary_share_percent = models.DecimalField('درصد سهم تکمیلی', max_digits=7, decimal_places=3, default=0)
    difference_percent = models.DecimalField('درصد مابه‌التفاوت', max_digits=7, decimal_places=3, default=0)
    class Meta: unique_together = [('service', 'insurance')]

    def __str__(self):
        return f'{self.service.name} — {self.insurance.name}'

    def total_amount(self):
        if self.pricing_method == self.PricingMethod.K_BASED:
            return (self.service.technical_k * self.technical_k_coefficient) + (self.service.professional_k * self.professional_k_coefficient)
        return self.fixed_total

    def apply_calculation(self):
        if self.share_mode != self.ShareMode.PERCENT:
            return
        total = self.total_amount()
        self.patient_share = (total * self.patient_share_percent / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        self.insurer_share = (total * self.insurer_share_percent / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        self.supplementary_share = (total * self.supplementary_share_percent / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
        self.difference_share = (total * self.difference_percent / 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP)

# Create your models here.
