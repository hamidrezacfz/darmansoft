from django.db import models


class FinancialEntry(models.Model):
    class Type(models.TextChoices):
        INCOME = 'income', 'درآمد'
        EXPENSE = 'expense', 'هزینه'

    entry_type = models.CharField('نوع سند', max_length=10, choices=Type)
    title = models.CharField('عنوان', max_length=160)
    category = models.CharField('سرفصل مالی', max_length=80, default='سایر')
    document_number = models.CharField('شماره سند / مرجع', max_length=60, blank=True)
    amount = models.DecimalField('مبلغ (ریال)', max_digits=14, decimal_places=0)
    entry_date = models.DateField('تاریخ سند')
    note = models.CharField('توضیحات', max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-entry_date', '-id']


class PurchaseInvoice(models.Model):
    supplier = models.CharField('نام فروشنده / تامین‌کننده', max_length=150)
    invoice_number = models.CharField('شماره فاکتور', max_length=50, blank=True)
    invoice_date = models.DateField('تاریخ فاکتور')
    total_amount = models.DecimalField('جمع مبلغ (ریال)', max_digits=14, decimal_places=0)
    note = models.CharField('توضیحات', max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-invoice_date', '-id']


class InventoryItem(models.Model):
    name = models.CharField('نام کالا', max_length=150, unique=True)
    unit = models.CharField('واحد شمارش', max_length=30, default='عدد')
    group = models.ForeignKey('InventoryGroup', null=True, blank=True, on_delete=models.PROTECT, verbose_name='گروه کالا')
    unit_definition = models.ForeignKey('InventoryUnit', null=True, blank=True, on_delete=models.PROTECT, verbose_name='واحد تعریف‌شده')
    expiration_date = models.DateField('تاریخ انقضا', null=True, blank=True)
    supplier = models.CharField('فروشنده / تأمین‌کننده', max_length=150, blank=True)
    ordered_by = models.CharField('سفارش‌دهنده', max_length=150, blank=True)
    requesting_department = models.CharField('بخش درخواست‌کننده', max_length=120, blank=True)
    quantity = models.DecimalField('موجودی فعلی', max_digits=12, decimal_places=2, default=0)
    reorder_point = models.DecimalField('حداقل موجودی', max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField('فعال', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryGroup(models.Model):
    name = models.CharField('نام گروه کالا', max_length=100, unique=True)
    active = models.BooleanField('فعال', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryUnit(models.Model):
    name = models.CharField('نام واحد', max_length=50, unique=True)
    active = models.BooleanField('فعال', default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class InventoryMovement(models.Model):
    class Type(models.TextChoices):
        IN = 'in', 'ورود کالا'
        OUT = 'out', 'خروج / مصرف'
        ADJUST = 'adjust', 'اصلاح موجودی'

    item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT, verbose_name='کالا')
    movement_type = models.CharField('نوع عملیات', max_length=10, choices=Type)
    quantity = models.DecimalField('تعداد', max_digits=12, decimal_places=2)
    unit_price = models.DecimalField('قیمت واحد (ریال)', max_digits=14, decimal_places=0, default=0)
    movement_date = models.DateField('تاریخ سند')
    destination_department = models.CharField('بخش مصرف‌کننده / مقصد', max_length=120, blank=True)
    document_number = models.CharField('شماره سند', max_length=60, blank=True)
    note = models.CharField('توضیحات', max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-movement_date', '-id']
