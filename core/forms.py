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

    class Meta:
        model = PawUser
        fields = ('email', 'profile_picture',
                  'language', 'telegram_username')
