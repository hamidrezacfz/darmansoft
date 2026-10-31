from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounts', '0002_userprofile_access_controls')]
    operations = [migrations.AlterField(
        model_name='userprofile', name='role',
        field=models.CharField(choices=[('admin', 'مدیر سیستم'), ('reception', 'پذیرش'), ('cashier', 'صندوق'), ('practitioner', 'پرسنل درمانی'), ('manager', 'مدیر مرکز'), ('finance', 'حسابداری / مالی'), ('insurance', 'مسئول بیمه'), ('scheduler', 'اپراتور نوبت‌دهی')], default='reception', max_length=20, verbose_name='نقش'),
    )]
