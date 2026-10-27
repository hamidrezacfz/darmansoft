from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('definitions', '0006_seed_practitioner_groups')]
    operations = [migrations.AddField(model_name='practitioner', name='medical_system_code', field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='کد نظام پزشکی / پرسنلی'))]
