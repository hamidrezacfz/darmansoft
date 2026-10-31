from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('definitions', '0009_tariff_calculation_options')]

    operations = [
        migrations.AddField(
            model_name='practitioner',
            name='active_panels',
            field=models.JSONField(blank=True, default=list, verbose_name='بخش‌های فعال'),
        ),
    ]
