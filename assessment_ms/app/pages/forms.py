# class Html5ModelForm(django.forms.ModelForm) taken from
# https://chase-seibert.github.io/blog/2010/09/03/django-html5-input-placeholders.html
# because ModelForm doesn't allow for HTML5 input placeholders (https://code.djangoproject.com/ticket/16304)

from django.forms import ModelForm, TextInput
from django.forms.utils import ErrorList


class Html5ModelForm(ModelForm):

    def as_table(self):
        return wrap_helptext_as_table(self)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None):

        super(Html5ModelForm, self).__init__(data, files, auto_id, prefix,
            initial, error_class, label_suffix,
            empty_permitted, instance)

        # create an HTML5 placeholder attribute based on the field help_text
        for field_name in self.fields:
            field = self.fields.get(field_name)
            if field:
                if type(field.widget) == TextInput:
                    field.widget.attrs["placeholder"] = field.help_text

