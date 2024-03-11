from django import forms
from .models import Ticket, Template, Team, Category
from django.utils.translation import gettext_lazy as _
import magic


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput(
            attrs={'class': 'file-input file-input-bordered w-full'}))
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class CommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'textarea textarea-bordered h-32', 'placeholder': 'Enter your comment here...'}))
    hidden_from_client = forms.BooleanField(widget=forms.CheckboxInput(
        attrs={'class': 'toggle toggle-error'}), required=False)


ATTACHMENT_CONTENT_TYPES = [
    'image/jpeg',
    'image/png',
    'application/pdf'
]


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'description', 'category', 'follow_up_to']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input input-bordered w-full', 'placeholder': _('Please enter a title'), 'aria-label': _('Title')}),
            'description': forms.Textarea(attrs={'class': 'textarea textarea-bordered h-32 w-full', 'placeholder': _('Please describe your issue'), 'aria-label': _('Description')}),
            'category': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'follow_up_to': forms.Select(attrs={'class': 'select select-bordered w-full'}),
        }

    def __init__(self, user, *args, **kwargs):
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['category'].empty_label = _('General')
        self.fields['follow_up_to'].empty_label = _('No Follow-up')
        self.fields['follow_up_to'].queryset = Ticket.objects.filter(
            status=Ticket.Status.CLOSED, user=user)

    attachments = MultipleFileField(required=False)

    def clean_attachments(self):
        files = self.cleaned_data.get('attachments')
        if files:
            for file in files:
                # Check file size
                if file.size > 1024 * 1024 * 5:
                    raise forms.ValidationError(
                        _('File size must be under 5MB.'))

                # Check file type
                uploaded_content_type = file.content_type
                mg = magic.Magic(mime=True)
                content_type = mg.from_buffer(file.read(1024))
                file.seek(0)

                if content_type != uploaded_content_type:
                    uploaded_content_type = content_type

                if uploaded_content_type not in ATTACHMENT_CONTENT_TYPES:
                    raise forms.ValidationError(
                        _('File type not supported. Supported types are: .jpg, .png, .pdf'))

        return files


class TemplateForm(forms.Form):

    template_select = forms.ModelChoiceField(queryset=Template.objects.all(), widget=forms.Select(
        attrs={'class': 'select select-bordered select-sm w-full'}))


class TeamAssignmentForm(forms.Form):
    team_select = forms.ModelChoiceField(queryset=Team.objects.all(), empty_label=_('No Team'), required=False, widget=forms.Select(
        attrs={'class': 'select select-bordered select-sm w-full'}))


class CategoryAssignmentForm(forms.Form):
    category_select = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label=_('General'), required=False, widget=forms.Select(
        attrs={'class': 'select select-bordered select-sm w-full'}))
