from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('definitions', '0008_service_category_panel_and_code'),
    ]

    operations = [
        migrations.AddField(model_name='medicalservice', name='technical_k', field=models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name='K فنی')),
        migrations.AddField(model_name='medicalservice', name='professional_k', field=models.DecimalField(decimal_places=4, default=0, max_digits=12, verbose_name='K حرفه‌ای')),
        migrations.AddField(model_name='insurancetariff', name='pricing_method', field=models.CharField(choices=[('fixed', 'مبلغ ثابت'), ('k_based', 'محاسبه بر اساس K')], default='fixed', max_length=12, verbose_name='روش محاسبه تعرفه')),
        migrations.AddField(model_name='insurancetariff', name='fixed_total', field=models.DecimalField(decimal_places=0, default=0, max_digits=14, verbose_name='مبلغ کل تعرفه (ریال)')),
        migrations.AddField(model_name='insurancetariff', name='technical_k_coefficient', field=models.DecimalField(decimal_places=0, default=0, max_digits=14, verbose_name='ضریب K فنی (ریال)')),
        migrations.AddField(model_name='insurancetariff', name='professional_k_coefficient', field=models.DecimalField(decimal_places=0, default=0, max_digits=14, verbose_name='ضریب K حرفه‌ای (ریال)')),
        migrations.AddField(model_name='insurancetariff', name='share_mode', field=models.CharField(choices=[('amount', 'مبلغ ریالی'), ('percent', 'درصد از مبلغ کل')], default='amount', max_length=10, verbose_name='روش ثبت سهم‌ها')),
        migrations.AddField(model_name='insurancetariff', name='difference_share', field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='مابه‌التفاوت (ریال)')),
        migrations.AddField(model_name='insurancetariff', name='patient_share_percent', field=models.DecimalField(decimal_places=3, default=0, max_digits=7, verbose_name='درصد سهم بیمار')),
        migrations.AddField(model_name='insurancetariff', name='insurer_share_percent', field=models.DecimalField(decimal_places=3, default=0, max_digits=7, verbose_name='درصد سهم سازمان')),
        migrations.AddField(model_name='insurancetariff', name='supplementary_share_percent', field=models.DecimalField(decimal_places=3, default=0, max_digits=7, verbose_name='درصد سهم تکمیلی')),
        migrations.AddField(model_name='insurancetariff', name='difference_percent', field=models.DecimalField(decimal_places=3, default=0, max_digits=7, verbose_name='درصد مابه‌التفاوت')),
    ]
