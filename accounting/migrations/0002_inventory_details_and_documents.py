import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounting', '0001_initial')]
    operations = [
        migrations.CreateModel(
            name='InventoryGroup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='نام گروه کالا')),
                ('active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='InventoryUnit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='نام واحد')),
                ('active', models.BooleanField(default=True, verbose_name='فعال')),
            ],
            options={'ordering': ['name']},
        ),
        migrations.AddField(model_name='inventoryitem', name='expiration_date', field=models.DateField(blank=True, null=True, verbose_name='تاریخ انقضا')),
        migrations.AddField(model_name='inventoryitem', name='ordered_by', field=models.CharField(blank=True, max_length=150, verbose_name='سفارش‌دهنده')),
        migrations.AddField(model_name='inventoryitem', name='requesting_department', field=models.CharField(blank=True, max_length=120, verbose_name='بخش درخواست‌کننده')),
        migrations.AddField(model_name='inventoryitem', name='supplier', field=models.CharField(blank=True, max_length=150, verbose_name='فروشنده / تأمین‌کننده')),
        migrations.AddField(model_name='inventoryitem', name='group', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.inventorygroup', verbose_name='گروه کالا')),
        migrations.AddField(model_name='inventoryitem', name='unit_definition', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounting.inventoryunit', verbose_name='واحد تعریف‌شده')),
        migrations.AddField(model_name='inventorymovement', name='destination_department', field=models.CharField(blank=True, max_length=120, verbose_name='بخش مصرف‌کننده / مقصد')),
        migrations.AddField(model_name='inventorymovement', name='document_number', field=models.CharField(blank=True, max_length=60, verbose_name='شماره سند')),
        migrations.AddField(model_name='inventorymovement', name='movement_date', field=models.DateField(default=datetime.date.today, verbose_name='تاریخ سند'), preserve_default=False),
        migrations.AlterModelOptions(name='inventorymovement', options={'ordering': ['-movement_date', '-id']}),
    ]
