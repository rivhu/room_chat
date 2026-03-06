from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Room


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'Email address'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-input'


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Room name (no spaces)', 'class': 'form-input'}),
            'description': forms.Textarea(attrs={'placeholder': 'Room description...', 'class': 'form-input', 'rows': 3}),
        }

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if ' ' in name:
            raise forms.ValidationError("Room name cannot contain spaces.")
        return name
