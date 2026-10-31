from django.db import migrations


LAB_TESTS = [
    ('700', 'شمارش کامل سلول‌های خون (CBC)'),
    ('701', 'قند خون ناشتا (FBS)'),
    ('702', 'قند خون دو ساعت بعد از غذا (2hpp)'),
    ('703', 'هموگلوبین گلیکوزیله (HbA1c)'),
    ('704', 'اوره خون (BUN)'),
    ('705', 'کراتینین (Cr)'),
    ('706', 'اسید اوریک'),
    ('707', 'کلسترول تام'),
    ('708', 'تری‌گلیسرید'),
    ('709', 'HDL کلسترول'),
    ('710', 'LDL کلسترول'),
    ('711', 'آزمایش کامل ادرار (U/A)'),
    ('712', 'کشت ادرار'),
    ('713', 'AST (SGOT)'),
    ('714', 'ALT (SGPT)'),
    ('715', 'آلکالین فسفاتاز (ALP)'),
    ('716', 'بیلی‌روبین تام و مستقیم'),
    ('717', 'TSH'),
    ('718', 'T4'),
    ('719', 'فریتین'),
    ('720', 'آهن سرم (Fe)'),
    ('721', 'ویتامین D (25-OH)'),
    ('722', 'آزمایش بارداری (BHCG)'),
    ('723', 'CRP'),
    ('724', 'ESR'),
]


def seed(apps, schema_editor):
    Category = apps.get_model('definitions', 'ServiceCategory')
    Service = apps.get_model('definitions', 'MedicalService')
    category, _ = Category.objects.get_or_create(
        code='LAB', defaults={'name': 'آزمایشگاه', 'panel': 'laboratory', 'active': True}
    )
    if category.panel != 'laboratory':
        category.panel = 'laboratory'
        category.save(update_fields=['panel'])
    for code, name in LAB_TESTS:
        Service.objects.get_or_create(
            code=code,
            defaults={
                'category': category,
                'name': name,
                'base_price': 0,
                'technical_k': 0,
                'professional_k': 0,
                'active': True,
            },
        )


def unseed(apps, schema_editor):
    Category = apps.get_model('definitions', 'ServiceCategory')
    Service = apps.get_model('definitions', 'MedicalService')
    codes = [code for code, _ in LAB_TESTS]
    Service.objects.filter(code__in=codes, category__code='LAB').delete()
    Category.objects.filter(code='LAB', name='آزمایشگاه').delete()


class Migration(migrations.Migration):
    dependencies = [('definitions', '0013_servicecategory_active')]
    operations = [migrations.RunPython(seed, unseed)]
