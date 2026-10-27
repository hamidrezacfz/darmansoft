from django.db import migrations, models
import django.db.models.deletion

SERVICES = [
 ('معاینه و تشخیص', [('معاینه اولیه و تشخیص', 'همه دندان‌ها'), ('مشاوره تخصصی دندانپزشکی', 'همه دندان‌ها'), ('طرح درمان', 'کل دهان')]),
 ('پیشگیری و جرم‌گیری', [('جرم‌گیری یک فک', 'فک بالا یا پایین'), ('جرم‌گیری کامل', 'کل دهان'), ('فلورایدتراپی', 'همه دندان‌ها'), ('فیشورسیلانت', 'دندان‌های خلفی')]),
 ('ترمیم', [('ترمیم کامپوزیت یک سطحی', 'یک دندان'), ('ترمیم کامپوزیت دو سطحی', 'یک دندان'), ('ترمیم کامپوزیت چندسطحی', 'یک دندان'), ('ترمیم آمالگام', 'یک دندان'), ('بازسازی تاج دندان', 'یک دندان')]),
 ('درمان ریشه', [('عصب‌کشی تک کانال', 'دندان قدامی'), ('عصب‌کشی دو کانال', 'پرمولر'), ('عصب‌کشی سه کانال', 'مولر'), ('درمان مجدد ریشه', 'یک دندان')]),
 ('جراحی', [('کشیدن دندان ساده', 'یک دندان'), ('کشیدن دندان نیمه نهفته', 'یک دندان'), ('جراحی دندان عقل نهفته', 'دندان عقل'), ('بخیه و کنترل خونریزی', 'ناحیه جراحی')]),
 ('پروتز و ایمپلنت', [('روکش دندان', 'یک دندان'), ('بریج دندانی', 'چند دندان'), ('پروتز متحرک کامل', 'فک بالا یا پایین'), ('ایمپلنت دندانی', 'یک دندان'), ('اباتمنت ایمپلنت', 'یک دندان')]),
 ('ارتودنسی', [('ویزیت ارتودنسی', 'کل دهان'), ('قالب‌گیری ارتودنسی', 'فک بالا و پایین'), ('نصب براکت', 'هر فک'), ('تنظیم ماهانه ارتودنسی', 'هر فک')]),
 ('تصویربرداری', [('رادیوگرافی پری‌اپیکال', 'یک دندان'), ('رادیوگرافی بایت‌وینگ', 'یک ناحیه'), ('رادیوگرافی پانورامیک', 'کل فک و صورت')]),
 ('دندانپزشکی کودکان', [('معاینه کودک', 'کل دهان'), ('ترمیم دندان شیری', 'یک دندان شیری'), ('کشیدن دندان شیری', 'یک دندان شیری'), ('فضانگهدارنده', 'یک ناحیه')]),
]

def seed(apps, schema_editor):
    Category = apps.get_model('definitions', 'ServiceCategory')
    Service = apps.get_model('definitions', 'MedicalService')
    Profile = apps.get_model('dentistry', 'DentalServiceProfile')
    number = 1
    for group, items in SERVICES:
        category, _ = Category.objects.get_or_create(name='دندانپزشکی - ' + group)
        for name, scope in items:
            code = f'DEN-{number:03d}'
            service, _ = Service.objects.get_or_create(code=code, defaults={'category_id': category.id, 'name': name, 'base_price': 0, 'active': True})
            Profile.objects.get_or_create(service_id=service.id, defaults={'tooth_scope': scope})
            number += 1

class Migration(migrations.Migration):
    initial = True
    dependencies = [('definitions', '0006_seed_practitioner_groups')]
    operations = [
        migrations.CreateModel(name='DentalServiceProfile', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('tooth_scope', models.CharField(blank=True, max_length=100, verbose_name='شماره / ناحیه دندان')),
            ('service', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dental_profile', to='definitions.medicalservice')),
        ]),
        migrations.RunPython(seed, migrations.RunPython.noop),
    ]
