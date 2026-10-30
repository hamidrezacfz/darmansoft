from django import forms
from .models import ServiceCategory, MedicalService, InsuranceProvider, InsuranceTariff, Practitioner, PractitionerGroup


class ServiceByCategorySelect(forms.Select):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        instance = getattr(value, 'instance', None)
        if instance is not None:
            option['attrs']['data-category'] = str(instance.category_id)
        return option
class CategoryForm(forms.ModelForm):
    class Meta: model = ServiceCategory; fields = ['code', 'name', 'panel']
class ServiceForm(forms.ModelForm):
    class Meta: model = MedicalService; fields = ['category','code','standard_code','name','technical_k','professional_k','active']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.all().order_by('panel', 'name')
class InsuranceForm(forms.ModelForm):
    class Meta: model = InsuranceProvider; fields = ['organization','name','active']
class TariffForm(forms.ModelForm):
    category = forms.ModelChoiceField(label='دستهٔ خدمت', queryset=ServiceCategory.objects.all(), required=False, empty_label='همهٔ دسته‌ها / انتخاب نشده')
    apply_to_category = forms.BooleanField(label='اعمال این فرمول برای همهٔ خدمات دسته', required=False)
    class Meta:
        model = InsuranceTariff
        fields = ['service', 'insurance', 'pricing_method', 'fixed_total', 'technical_k_coefficient', 'professional_k_coefficient', 'share_mode', 'patient_share', 'insurer_share', 'supplementary_share', 'difference_share', 'patient_share_percent', 'insurer_share_percent', 'supplementary_share_percent', 'difference_percent']

    def clean(self):
        cleaned = super().clean()
        for field in ('fixed_total', 'technical_k_coefficient', 'professional_k_coefficient', 'patient_share', 'insurer_share', 'supplementary_share', 'difference_share', 'patient_share_percent', 'insurer_share_percent', 'supplementary_share_percent', 'difference_percent'):
            if cleaned.get(field) is None:
                cleaned[field] = 0
        category, service = cleaned.get('category'), cleaned.get('service')
        if cleaned.get('apply_to_category') and not category:
            self.add_error('category', 'برای اعمال گروهی، دستهٔ خدمت را انتخاب کنید.')
        elif not cleaned.get('apply_to_category') and not service:
            self.add_error('service', 'خدمت را انتخاب کنید یا اعمال گروهی را فعال کنید.')
        elif category and service and service.category_id != category.id:
            self.add_error('service', 'خدمت انتخاب‌شده متعلق به دستهٔ انتخابی نیست.')
        if cleaned.get('pricing_method') == InsuranceTariff.PricingMethod.K_BASED:
            if not (cleaned.get('technical_k_coefficient') or cleaned.get('professional_k_coefficient')):
                self.add_error('technical_k_coefficient', 'حداقل یکی از ضرایب K را وارد کنید.')
        elif not cleaned.get('fixed_total'):
            self.add_error('fixed_total', 'مبلغ کل تعرفه را وارد کنید.')
        if cleaned.get('share_mode') == InsuranceTariff.ShareMode.PERCENT:
            percent_total = sum(cleaned.get(field) or 0 for field in ('patient_share_percent', 'insurer_share_percent', 'supplementary_share_percent', 'difference_percent'))
            if percent_total > 100:
                raise forms.ValidationError('جمع درصد سهم‌ها نمی‌تواند بیشتر از ۱۰۰ باشد.')
        return cleaned

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ServiceCategory.objects.all().order_by('panel', 'name')
        self.fields['service'].queryset = MedicalService.objects.filter(active=True).select_related('category').order_by('category__name', 'name')
        self.fields['service'].required = False
        self.fields['service'].widget = ServiceByCategorySelect()
        for field in ('fixed_total', 'technical_k_coefficient', 'professional_k_coefficient', 'patient_share', 'insurer_share', 'supplementary_share', 'difference_share', 'patient_share_percent', 'insurer_share_percent', 'supplementary_share_percent', 'difference_percent'):
            self.fields[field].required = False

    def save(self, commit=True):
        tariff = super().save(commit=False)
        tariff.apply_calculation()
        if commit:
            tariff.save()
        return tariff

    def tariff_values(self):
        return {field: self.cleaned_data[field] for field in ('insurance', 'pricing_method', 'fixed_total', 'technical_k_coefficient', 'professional_k_coefficient', 'share_mode', 'patient_share', 'insurer_share', 'supplementary_share', 'difference_share', 'patient_share_percent', 'insurer_share_percent', 'supplementary_share_percent', 'difference_percent')}
class PractitionerGroupForm(forms.ModelForm):
    class Meta: model = PractitionerGroup; fields = ['name','active']
class PractitionerForm(forms.ModelForm):
    class Meta: model = Practitioner; fields = ['name','medical_system_code','group','role','share_percent','active']
    def clean_medical_system_code(self):
        return self.cleaned_data['medical_system_code'].strip() or None
