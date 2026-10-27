from django import forms
from django.contrib.auth.models import User
from .models import UserProfile
class UserForm(forms.Form):
    username=forms.CharField(label='نام کاربری')
    password=forms.CharField(label='رمز عبور',widget=forms.PasswordInput)
    role=forms.ChoiceField(label='سطح دسترسی',choices=UserProfile.Role.choices)
    def clean_username(self):
        value=self.cleaned_data['username']
        if User.objects.filter(username=value).exists(): raise forms.ValidationError('این نام کاربری قبلاً ثبت شده است.')
        return value
