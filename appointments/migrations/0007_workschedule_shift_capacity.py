from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('appointments', '0006_workschedule')]
    operations = [
        migrations.AddField(model_name='workschedule', name='shift_name', field=models.CharField(blank=True, max_length=30, verbose_name='عنوان شیفت')),
        migrations.AddField(model_name='workschedule', name='capacity', field=models.PositiveIntegerField(default=1, verbose_name='ظرفیت نوبت شیفت')),
    ]
