from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('accounts', '0001_initial')]
    operations = [
        migrations.AddField(model_name='userprofile', name='active_panels', field=models.JSONField(blank=True, default=list, verbose_name='پنل‌های فعال')),
        migrations.AddField(model_name='userprofile', name='permissions', field=models.JSONField(blank=True, default=list, verbose_name='دسترسی‌های قابل تنظیم')),
    ]
