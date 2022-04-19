from django import forms
from django.utils.translation import gettext_lazy as _

from wiki.plugins.attachments import models


class AttachmentForm(forms.ModelForm):
    
    description = forms.CharField(label=_('Description'),
                                  help_text=_('A short summary of what the file contains'),
                                  required=False)
    
    class Meta:
        model = models.AttachmentRevision
        fields = ('file', 'description',)

class DeleteForm(forms.Form):
    """This form is both used for dereferencing and deleting attachments"""
    confirm = forms.BooleanField(label=_('Yes I am sure...'),
                                 required=False)
    
    def clean_confirm(self):
        if not self.cleaned_data['confirm']:
            raise forms.ValidationError(_('You are not sure enough!'))
        return True

class SearchForm(forms.Form):
    
    query = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'search-query'}),)
