from django.db import migrations


def seed_groups(apps, schema_editor):
    PractitionerGroup = apps.get_model('definitions', 'PractitionerGroup')
    for name in ('پزشک', 'پرستار', 'کارشناس', 'اپراتور'):
        PractitionerGroup.objects.get_or_create(name=name)


class Migration(migrations.Migration):
    dependencies = [('definitions', '0005_practitioner_groups_standard_codes_and_supplementary')]
    operations = [migrations.RunPython(seed_groups, migrations.RunPython.noop)]
