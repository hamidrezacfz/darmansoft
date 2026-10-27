from django import forms
from .models import Payment
from reception.models import Admission

class PaymentForm(forms.Form):
    referral_code = forms.CharField(label='کد ارجاع به صندوق', max_length=20, widget=forms.TextInput(attrs={'placeholder':'کد پایان پذیرش'}))
    method = forms.ChoiceField(label='روش پرداخت', choices=Payment.Method.choices)
    note = forms.CharField(label='شرح', required=False, max_length=200)
    def clean_referral_code(self):
        code = self.cleaned_data['referral_code'].strip()
        try: self.admission = Admission.objects.select_related('patient','service').get(tracking_code=code, status=Admission.Status.OPEN)
        except Admission.DoesNotExist: raise forms.ValidationError('پذیرش باز با این کد پیدا نشد یا قبلاً تسویه شده است.')
        return code
