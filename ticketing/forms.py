from django import forms
from .models import Ticket, Template, Team, Category
from django.utils.translation import gettext_lazy as _


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'textarea textarea-bordered h-32', 'placeholder': 'Enter your comment here...'}))
    hidden_from_client = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'toggle toggle-error'}), required=False)


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': _('Please enter a title'), 'aria-label': _('Title')}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered h-32 w-full', 'placeholder': _('Please describe your issue'), 'aria-label': _('Description')}),
            'category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }

    def __init__(self, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['category'].empty_label = _('General')


class TemplateForm(forms.Form):

    template_select = forms.ModelChoiceField(queryset=Template.objects.all(), widget=forms.Select(
        attrs={'class': 'select select-bordered select-sm w-full'}))


class TeamAssignmentForm(forms.Form):
    team_select = forms.ModelChoiceField(queryset=Team.objects.all(), empty_label=_('No Team'), required=False, widget=forms.Select(
        attrs={'class': 'select select-bordered select-sm w-full'}))


class CategoryAssignmentForm(forms.Form):
    category_select = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=_('General'), required=False, widget=forms.Select(
        attrs={'class': 'select select-bordered select-sm w-full'}))
