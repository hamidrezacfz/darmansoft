from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('definitions', '0011_insurance_panel_k_coefficients')]
    operations = [
        migrations.AlterField(
            model_name='servicecategory', name='panel',
            field=models.CharField(choices=[('general', 'پذیرش عمومی'), ('dentistry', 'دندان‌پزشکی'), ('imaging', 'تصویربرداری'), ('aesthetics', 'زیبایی و سلامت'), ('laboratory', 'آزمایشگاه'), ('physiotherapy', 'فیزیوتراپی'), ('pharmacy', 'داروخانه')], default='general', max_length=20, verbose_name='پنل مربوطه'),
        ),
    ]
