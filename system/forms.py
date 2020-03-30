from django import forms
from django.forms import modelform_factory
from .models import TADuty, TA


class DutyCreateForm(forms.ModelForm):
    class Meta:
        model = TADuty
        fields = ('labNumber', 'preparationHour', 'labHour', 'labWorkingHour', 'assignmentNumber',
                  'assignmentWorkingHour', 'contactHour', 'otherDutiesHour')


class DocumentForm(forms.Form):
    docfile = forms.FileField(
        label='Select a file',
        help_text='max. 42 megabytes'
    )
