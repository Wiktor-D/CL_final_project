from django import forms

from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model, authenticate
from .models import Profile, UserAddress
from localflavor.pl.forms import PLPostalCodeField

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
        help_texts = {
            'username': ''
        }

    def clean(self):
        cd = super().clean()
        pass1 = cd.get('password')
        pass2 = cd.get('password2')
        if pass1 != pass2:
            raise ValidationError('Password must be identical!')

    def clean_email(self):
        cd = self.cleaned_data['email']
        if User.objects.filter(email=cd).exists():
            raise ValidationError('this email already exists')
        return cd



class SearchForm(forms.Form):
    query = forms.CharField(label='')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['birthdate', 'avatar']


class UserAddressForm(forms.ModelForm):
    postal_code = PLPostalCodeField()

    class Meta:
        model = UserAddress
        fields = ['city', 'street', 'building_nr', 'apartment_nr', 'postal_code', 'is_billing_addr', 'is_shipping_addr']


class CartAddRecipeForm(forms.Form):

    amount = forms.FloatField
    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)
