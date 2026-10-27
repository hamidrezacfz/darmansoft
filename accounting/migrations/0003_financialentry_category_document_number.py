from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounting', '0002_inventory_details_and_documents')]

    operations = [
        migrations.AddField(
            model_name='financialentry', name='category',
            field=models.CharField(default='سایر', max_length=80, verbose_name='سرفصل مالی'),
        ),
        migrations.AddField(
            model_name='financialentry', name='document_number',
            field=models.CharField(blank=True, max_length=60, verbose_name='شماره سند / مرجع'),
        ),
    ]
