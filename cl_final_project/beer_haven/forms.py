from django import forms

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cd = super().clean()
        username = cd.get('username')
        password = cd.get('password')
        self.user = authenticate(username=username, password=password)
        if self.user is None:
            raise ValidationError('Incorrect login or password!')


class UserRegistrationForm(forms.ModelForm):

    email = forms.EmailField(label='Email')
    password2 = forms.CharField(label='Repeat Password', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'password2',
        ]
        widgets = {
            'password': forms.PasswordInput
        }

    def clean(self):
        cd = super().clean()
        pass1 = cd.get('password')
        pass2 = cd.get('password2')
        if pass1 != pass2:
            raise ValidationError('Password must be identical!')

class SearchForm(forms.Form):
    query = forms.CharField(label='')
