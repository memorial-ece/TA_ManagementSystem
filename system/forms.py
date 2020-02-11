from django import forms
from .models import TADuty


class DutyCreateForm(forms.ModelForm):
    class Meta:
        model = TADuty
        fields = ('labNumber', 'preparationHour', 'labHour', 'labWorkingHour', 'assignmentNumber',
                  'assignmentWorkingHour', 'contactHour', 'otherDutiesHour')
