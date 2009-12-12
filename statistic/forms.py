from django import forms
from lib.forms import MonthPickerField
from datetime import date

class MonthForm(forms.Form):
    
    #month = forms.ChoiceField(choices=[(i+1, name) for i, name in enumerate(month_name[1:])],
    #    initial=date.today().month)
    month = MonthPickerField(initial=date.today())
    
    def __init__(self, *args, **kwargs):
        st = kwargs['start_year']
        del kwargs['start_year']
        super(MonthForm, self).__init__(*args, **kwargs)
        self.fields['month'].widget.attrs.update({'start_year': st})