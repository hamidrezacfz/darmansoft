from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('definitions', '0012_insurance_k_and_future_panels')]
    operations = [migrations.AddField(model_name='servicecategory', name='active', field=models.BooleanField(default=True, verbose_name='فعال'))]
