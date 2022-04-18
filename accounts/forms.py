from django import forms

class StellarAccountForm(forms.Form):
   
    Deposit = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder' : 'amount (NGN)',
            'class' : 'form-control',
        },
    ))
    NGNT = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder' : 'amount NGNT',
            'class' : 'form-control',
            'readonly' : True,
            'disabled': True,
            'required': False
        },
    ))