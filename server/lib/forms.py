from django.forms.widgets import MultiWidget, HiddenInput
from django.forms.fields import MultiValueField, IntegerField
from django.utils.safestring import mark_safe
import datetime 

class MonthPickerWindget(MultiWidget):

    class Media:
        js = (
            "media/monthpicker/monthpicker.js",
            "media/monthpicker/widget.js"
        )
        css = {
            'all': ("media/monthpicker/monthpicker.css",)
        }

    def __init__(self, attrs=None):
        widgets = (HiddenInput(attrs=attrs), HiddenInput(attrs=attrs))
        super(MonthPickerWindget, self).__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value.year, value.month]
        return [None, None]

    def render(self, *args, **kwargs):
        output = []
        output.append(super(MonthPickerWindget, self).render(*args, **kwargs))
        output.append('<div id="mounth_picker" class="MonthPicker">%s</div>' % self.attrs.get('start_year', 2000))
        return mark_safe(''.join(output))

class MonthPickerField(MultiValueField):
    widget = MonthPickerWindget

    def __init__(self, *args, **kwargs):
        fields = (
            IntegerField(max_value=datetime.date.today().year, min_value=1900),
            IntegerField(max_value=12, min_value=1),
        )
        super(MonthPickerField, self).__init__(fields, *args, **kwargs)

    def compress(self, data):
        if data:
            return datetime.date(data[0], data[1], 1)
        return None