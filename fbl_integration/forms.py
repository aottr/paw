from typing import Any
from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from datetime import datetime

class FblAuthForm(forms.Form):
    badge_number = forms.CharField(required=True)
    dob = forms.CharField(required=True)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super(FblAuthForm, self).clean()
        badge_number = cleaned_data.get("badge_number")
        dob = cleaned_data.get("dob")

        if not badge_number:
            raise forms.ValidationError(
            _("Badge number is required")
            )
        
        try:
            int(badge_number)
        except ValueError:
            raise forms.ValidationError(
            _("Badge number must be a number")
            )
        
        if not dob:
            raise forms.ValidationError(
                _("Date of birth is required")
            )
        try:
            dob = datetime.strptime(dob, "%d/%m/%Y").strftime("%Y-%m-%d")
        except ValueError:
            raise forms.ValidationError(
            _("Date of birth must be in the format DD/MM/YYYY")
            )
        cleaned_data["dob"] = dob

        return cleaned_data
    
class FblAuthCodeForm(FblAuthForm):
    validation_code = forms.CharField(required=True)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super(FblAuthCodeForm, self).clean()
        validation_code = cleaned_data.get("validation_code")

        if not validation_code:
            raise forms.ValidationError(
                _("The validation code is required. Please check your emails.")
            )
        
        return cleaned_data
    
class RegistrationCompletionForm(forms.Form):
    email = forms.EmailField(required=True)

    def clean(self) -> dict[str, Any]:
        cleaned_data = super(RegistrationCompletionForm, self).clean()
        email = cleaned_data.get("email")

        if not email:
            raise forms.ValidationError(
                _("A Mail is required for notifications.")
            )
        
        return cleaned_data