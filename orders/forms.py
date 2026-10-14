from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
class RegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'password1', 'password2']
class QuantityForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=20)
class CheckoutForm(forms.Form):
    address = forms.CharField(min_length=10, max_length=500, widget=forms.Textarea(attrs={'rows': 3}), label='Delivery address')
    phone = forms.CharField(max_length=20, validators=[RegexValidator(r'^\+?[0-9]{10,15}$', 'Enter 10–15 digits, optionally starting with +.')], label='Contact number')
    token = forms.UUIDField(widget=forms.HiddenInput)
