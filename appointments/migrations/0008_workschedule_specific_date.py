from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('appointments', '0007_workschedule_shift_capacity')]
    operations = [migrations.AddField(model_name='workschedule', name='schedule_date', field=models.DateField(blank=True, null=True, verbose_name='تاریخ مشخص'))]
