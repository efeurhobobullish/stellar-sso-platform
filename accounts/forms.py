from django import forms

class StellarAccountForm(forms.Form):
   
    Deposit = forms.DecimalField(widget=forms.NumberInput(
        attrs={
            'placeholder' : 'amount (NGN)',
            'class' : 'form-control',
        },
    ))
    NGNT = forms.DecimalField(required=False, widget=forms.NumberInput(
        attrs={
            'placeholder' : 'amount NGNT',
            'class' : 'form-control',
            'readonly' : True,
            'disabled': True,
        },
    ))
    trx_ref = forms.CharField(required=False)