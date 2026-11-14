from django import forms
from django.contrib.auth.models import User
from project.Models.Ticket import Ticket
from django.db.models import Q
from project.Models.Ticket import TicketComment

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'customer', 'category', 'priority', 'status', 'assigned_agent', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;'}),

            'customer': forms.Select(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;'}),

            'category': forms.Select(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;'}),

            'priority': forms.Select(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;'}),

            'status': forms.Select(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;'}),

            'assigned_agent': forms.Select(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;'}),
            
            'description': forms.Textarea(attrs={'style': 'width:100%; padding:14px; font-size:16px; border:2px solid #ddd; border-radius:8px;', 'rows': 4}),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_agent'].queryset = User.objects.filter(
            Q(is_staff=True) | Q(is_superuser=True)
        ).distinct()

        if user is not None:
            if user.is_superuser:
                pass
            elif user.is_staff:
                self.fields.pop('assigned_agent')
            else:
                for f in ['customer', 'priority', 'status', 'assigned_agent']:
                    self.fields.pop(f)

        # Force customer to be required whenever it's present on the form
        if 'customer' in self.fields:
            self.fields['customer'].required = True

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        return title
    
    def clean(self):
        cleaned_data = super().clean()
        new_status = cleaned_data.get('status')
        description = cleaned_data.get('description', '').strip()

        
        if self.instance.pk and new_status != self.instance.status:
            if not description:
                self.add_error('description', 'Please describe the issue and update when changing status.')

        return cleaned_data

class StatusChangeForm(forms.Form):
    new_status = forms.ChoiceField(choices=[
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ])
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe the issue and what was done...'}),
        required=True,
        error_messages={'required': 'Please explain the issue and update before changing status.'}
    )


class TicketCommentForm(forms.Form):
    comment = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        required=True,
    )

class TicketReplyForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Write a reply for your team...',
                'style': 'width:100%; padding:10px; font-size:14px; border:1px solid #ccc; border-radius:6px;'
            })
        }