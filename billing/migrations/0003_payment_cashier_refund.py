from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [('billing', '0002_payment_admission'), ('auth', '0012_alter_user_first_name_max_length')]
    operations = [
        migrations.AddField(model_name='payment', name='cashier', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cashier_payments', to=settings.AUTH_USER_MODEL, verbose_name='کاربر صندوق')),
        migrations.CreateModel(name='PaymentRefund', fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ('amount', models.DecimalField(decimal_places=0, max_digits=12, verbose_name='مبلغ مستردشده (ریال)')),
            ('note', models.CharField(blank=True, max_length=200, verbose_name='شرح استرداد')),
            ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='زمان استرداد')),
            ('payment', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='refund', to='billing.payment', verbose_name='پرداخت')),
            ('refunded_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='payment_refunds', to=settings.AUTH_USER_MODEL, verbose_name='کاربر مستردکننده')),
        ]),
    ]
