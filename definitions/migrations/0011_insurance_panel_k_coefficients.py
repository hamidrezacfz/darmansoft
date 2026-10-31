from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('definitions', '0010_practitioner_active_panels')]
    operations = [migrations.AddField(model_name='insuranceprovider', name='panel_k_coefficients', field=models.JSONField(blank=True, default=dict, verbose_name='ضرایب K پنل‌ها'))]
