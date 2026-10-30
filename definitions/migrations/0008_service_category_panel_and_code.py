from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0007_practitioner_medical_system_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='servicecategory',
            name='panel',
            field=models.CharField(
                choices=[
                    ('general', 'پذیرش عمومی'),
                    ('dentistry', 'دندان‌پزشکی'),
                    ('imaging', 'تصویربرداری'),
                    ('aesthetics', 'زیبایی و سلامت'),
                ],
                default='general',
                max_length=20,
                verbose_name='پنل مربوطه',
            ),
        ),
        migrations.AddField(
            model_name='servicecategory',
            name='code',
            field=models.CharField(default='', max_length=20, unique=True, verbose_name='کد دسته'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='medicalservice',
            name='base_price',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='تعرفه آزاد (ریال)'),
        ),
    ]
