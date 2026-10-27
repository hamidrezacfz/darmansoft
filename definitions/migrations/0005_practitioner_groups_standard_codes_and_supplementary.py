import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('definitions', '0004_practitioner')]
    operations = [
        migrations.CreateModel(
            name='PractitionerGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80, unique=True, verbose_name='نام گروه')),
                ('active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={'verbose_name': 'گروه پرسنل', 'verbose_name_plural': 'گروه‌های پرسنل'},
        ),
        migrations.AddField(model_name='medicalservice', name='standard_code', field=models.CharField(blank=True, max_length=30, null=True, unique=True, verbose_name='کد استاندارد خدمت')),
        migrations.AddField(model_name='practitioner', name='group', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='definitions.practitionergroup', verbose_name='گروه شغلی')),
        migrations.AddField(model_name='practitioner', name='share_percent', field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='درصد سهم از عملکرد')),
        migrations.AddField(model_name='insurancetariff', name='supplementary_share', field=models.DecimalField(decimal_places=0, default=0, max_digits=12, verbose_name='سهم بیمه تکمیلی (ریال)')),
    ]
