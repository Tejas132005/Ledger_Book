from django import forms
from .models import User


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Create a strong password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control', 'placeholder': 'Re-enter password'
    }))

    class Meta:
        model = User
        fields = ['business_name', 'phone_number', 'email', 'password']
        widgets = {
            'business_name': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. Sharma Traders'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. 9876543210'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 'placeholder': 'e.g. name@example.com'
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.username = self.cleaned_data["phone_number"]
        if commit:
            user.save()
        return user


class UserLoginForm(forms.Form):
    login_id = forms.CharField(
        label="Phone Number or Business Name",
        widget=forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Phone or Business Name'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control', 'placeholder': 'Your password'
        })
    )
