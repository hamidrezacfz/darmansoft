from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('reception', '0003_admission_practitioner')]
    operations = [migrations.AddField(model_name='admission', name='supplementary_share', field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='مبلغ سهم بیمه تکمیلی'))]
