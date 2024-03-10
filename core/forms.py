from django import forms
from django.conf import settings
from .models import PawUser


class UserChangeForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'input input-bordered w-full'}))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(
        attrs={'class': 'file-input file-input-bordered w-full'}))
    language = forms.ChoiceField(choices=settings.LANGUAGES, widget=forms.Select(
        attrs={'class': 'select select-bordered w-full'}))
    telegram_username = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'grow', 'placeholder': 'Telegram Username'}))
    use_darkmode = forms.BooleanField(
        required=False, widget=forms.CheckboxInput(attrs={'class': 'toggle toggle-secondary'}))

    class Meta:
        model = PawUser
        fields = ('email', 'profile_picture',
                  'language', 'telegram_username', 'use_darkmode')


class RegisterForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'input input-bordered w-full'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(
        attrs={'class': 'input input-bordered w-full'}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'input input-bordered w-full'}))
    password_confirm = forms.CharField(required=True, widget=forms.PasswordInput(
        attrs={'class': 'input input-bordered w-full'}))

    class Meta:
        model = PawUser
        fields = ('username', 'email', 'password')

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password != password_confirm:
            raise forms.ValidationError(
                "password and password_confirm does not match"
            )
        if len(password) < 10:
            raise forms.ValidationError(
                "password must be at least 10 characters long"
            )

        if PawUser.objects.filter(username=cleaned_data.get("username")).exists():
            raise forms.ValidationError(
                "An account with this username already exists"
            )
        if PawUser.objects.filter(email=cleaned_data.get("email")).exists():
            raise forms.ValidationError(
                "An account with this email already exists"
            )
        return cleaned_data


class AccountFinishForm(forms.Form):
    username = forms.CharField(required=True, widget=forms.TextInput(
        attrs={'class': 'input input-bordered w-full'}))

    class Meta:
        model = PawUser
        fields = ('username')

    def clean(self):
        cleaned_data = super(AccountFinishForm, self).clean()

        if PawUser.objects.filter(username=cleaned_data.get("username")).exists():
            raise forms.ValidationError(
                "An account with this username already exists"
            )

        return cleaned_data
