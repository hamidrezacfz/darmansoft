from django.db import models
from patients.models import Patient
class MedicalRecord(models.Model):
    patient=models.ForeignKey(Patient,on_delete=models.PROTECT,verbose_name='بیمار')
    complaint=models.CharField('علت مراجعه',max_length=250)
    diagnosis=models.CharField('تشخیص',max_length=250,blank=True)
    notes=models.TextField('یادداشت درمانی',blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    class Meta: ordering=['-created_at']

# Create your models here.
