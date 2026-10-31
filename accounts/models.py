from django.db import models
from django.contrib.auth.models import User
class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN='admin','مدیر سیستم'
        RECEPTION='reception','پذیرش'
        CASHIER='cashier','صندوق'
        PRACTITIONER='practitioner','پرسنل درمانی'
        MANAGER='manager','مدیر مرکز'
        FINANCE='finance','حسابداری / مالی'
        INSURANCE='insurance','مسئول بیمه'
        SCHEDULER='scheduler','اپراتور نوبت‌دهی'
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    role=models.CharField('نقش',max_length=20,choices=Role,default=Role.RECEPTION)
    active_panels=models.JSONField('پنل‌های فعال',default=list,blank=True)
    permissions=models.JSONField('دسترسی‌های قابل تنظیم',default=list,blank=True)
    def __str__(self): return f'{self.user.username} - {self.get_role_display()}'

# Create your models here.
