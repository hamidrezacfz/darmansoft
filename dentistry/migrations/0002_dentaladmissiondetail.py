from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('dentistry', '0001_dentalserviceprofile_and_seed')]
    operations = [migrations.CreateModel(name='DentalAdmissionDetail', fields=[
        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        ('tooth_numbers', models.CharField(blank=True, max_length=150, verbose_name='دندان‌های انتخاب‌شده')),
        ('note', models.TextField(blank=True, verbose_name='توضیحات دندانپزشکی')),
        ('admission', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='dental_detail', to='reception.admission')),
    ])]
