from django import forms
from project.Models import Customer

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email','password', 'phone', 'company', 'status']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            if not (phone.isascii() and phone.isdigit()):
                raise forms.ValidationError("Only digits (0-9) are allowed.")
            if len(phone) != 10:
                raise forms.ValidationError("Phone number must be exactly 10 digits.")
        return phone


