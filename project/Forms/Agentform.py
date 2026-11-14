from django import forms
from django.contrib.auth.models import User


class AgentForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        help_text="Set an initial password for this agent."
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_username(self):
        username = self.cleaned_data['username'].strip()
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_staff = True
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user