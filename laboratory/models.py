from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient
from definitions.models import MedicalService, Practitioner
from reception.models import Admission

class LaboratoryOrder(models.Model):
    class Status(models.TextChoices):
        ORDERED='ordered','ثبت درخواست'; COLLECTED='collected','نمونه‌گیری‌شده'; RECEIVED='received','دریافت‌شده'; IN_PROCESS='in_process','در حال انجام'; VERIFIED='verified','تأییدشده'; RELEASED='released','گزارش صادرشده'; REJECTED='rejected','رد نمونه'; CANCELLED='cancelled','لغوشده'
    patient=models.ForeignKey(Patient,on_delete=models.PROTECT,related_name='laboratory_orders')
    practitioner=models.ForeignKey(Practitioner,null=True,blank=True,on_delete=models.PROTECT)
    referring_practitioner_name=models.CharField('نام پزشک ارجاع‌دهنده',max_length=120,blank=True)
    accession_number=models.CharField('شماره پذیرش آزمایشگاه',max_length=24,unique=True)
    priority=models.CharField('اولویت',max_length=12,choices=[('normal','عادی'),('urgent','فوری'),('emergency','اورژانسی')],default='normal')
    status=models.CharField('وضعیت',max_length=20,choices=Status.choices,default=Status.ORDERED)
    notes=models.TextField('توضیحات پزشک',blank=True)
    created_by=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']
    def __str__(self): return f'{self.accession_number} - {self.patient}'

class LaboratorySpecimen(models.Model):
    order=models.ForeignKey(LaboratoryOrder,on_delete=models.CASCADE,related_name='specimens')
    specimen_type=models.CharField('نوع نمونه',max_length=80)
    barcode=models.CharField('بارکد نمونه',max_length=40,unique=True)
    collected_at=models.DateTimeField(null=True,blank=True); received_at=models.DateTimeField(null=True,blank=True)
    collector=models.CharField('نمونه‌گیرنده',max_length=100,blank=True)
    status=models.CharField('وضعیت نمونه',max_length=12,choices=[('pending','در انتظار نمونه'),('collected','نمونه‌گیری‌شده'),('received','دریافت‌شده'),('rejected','ردشده')],default='pending')
    rejection_reason=models.CharField('علت رد نمونه',max_length=200,blank=True)

class LaboratoryOrderTest(models.Model):
    order=models.ForeignKey(LaboratoryOrder,on_delete=models.CASCADE,related_name='tests')
    service=models.ForeignKey(MedicalService,on_delete=models.PROTECT)
    admission=models.ForeignKey(Admission,null=True,blank=True,on_delete=models.PROTECT)
    result=models.CharField('نتیجه',max_length=255,blank=True); unit=models.CharField('واحد',max_length=40,blank=True); reference_range=models.CharField('محدوده مرجع',max_length=100,blank=True); flag=models.CharField('وضعیت نتیجه',max_length=20,blank=True)
    result_status=models.CharField('وضعیت نتیجه',max_length=12,choices=[('pending','در انتظار نتیجه'),('entered','نتیجه واردشده'),('verified','تأییدشده')],default='pending')
    verified_by=models.ForeignKey(User,null=True,blank=True,on_delete=models.SET_NULL,related_name='verified_lab_results'); verified_at=models.DateTimeField(null=True,blank=True)

class LaboratoryReferenceRange(models.Model):
    service = models.ForeignKey(MedicalService, on_delete=models.CASCADE, related_name='laboratory_ranges')
    gender = models.CharField('جنسیت', max_length=10, blank=True)
    age_min = models.PositiveSmallIntegerField('حداقل سن', default=0)
    age_max = models.PositiveSmallIntegerField('حداکثر سن', default=150)
    minimum = models.DecimalField('حداقل رنج', max_digits=12, decimal_places=4, null=True, blank=True)
    maximum = models.DecimalField('حداکثر رنج', max_digits=12, decimal_places=4, null=True, blank=True)
    unit = models.CharField('واحد', max_length=40, blank=True)
    critical_low = models.DecimalField('حد بحرانی پایین', max_digits=12, decimal_places=4, null=True, blank=True)
    critical_high = models.DecimalField('حد بحرانی بالا', max_digits=12, decimal_places=4, null=True, blank=True)
    active = models.BooleanField('فعال', default=True)

class LaboratoryWorklist(models.Model):
    name = models.CharField('نام لیست کاری', max_length=100)
    section = models.CharField('بخش آزمایشگاه', max_length=80, blank=True)
    services = models.ManyToManyField(MedicalService, related_name='laboratory_worklists', blank=True)
    active = models.BooleanField('فعال', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
