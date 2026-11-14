from django import forms
from project.Models.Customer import Customer,Follow_up
from project.Models.Ticket import Ticket
 


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



class CustomerFollowUpForm(forms.ModelForm):
    class Meta:
        model = Follow_up
        fields = ["ticket", "Follow_up_date", "notes", "assigned_agent", "status"]
        widgets = {
            "Follow_up_date": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }
 
    def __init__(self, *args, customer=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["ticket"].required = False
        if customer is not None:
            # Only show this customer's own tickets in the dropdown
            self.fields["ticket"].queryset = customer.tickets.all()  # adjust related_name if different
        # Show "Title — Status" in the dropdown instead of just the ticket's __str__
        self.fields["ticket"].label_from_instance = lambda t: f"{t.title} — {t.get_status_display()}"
 