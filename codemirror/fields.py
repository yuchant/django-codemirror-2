from django.db import models
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import simplejson as json
from django.utils.translation import ugettext_lazy as _

from django.forms.fields import Field
from django.forms.util import ValidationError as FormValidationError

from codemirror.widgets import CodeMirrorJSONWidget
from codemirror.widgets import CodeMirrorUploadWidget
from codemirror.widgets import YAMLCodeMirrorAJAXUploadWidget


class JSONFormField(Field):
    # widget = CodeMirrorJSONWidget
    
    def clean(self, value):
        if not value and not self.required:
            return None

        value = super(JSONFormField, self).clean(value)
        
        try:
            json.loads(value)
        except ValueError:
            raise FormValidationError(_("Enter valid JSON"))
        return value


class JSONCodeMirrorField(models.TextField):
    """JSONField is a generic textfield that serializes/unserializes JSON objects"""

    # Used so to_python() is called
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        self.dump_kwargs = kwargs.pop('dump_kwargs', {'cls': DjangoJSONEncoder})
        self.load_kwargs = kwargs.pop('load_kwargs', {})

        super(JSONCodeMirrorField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        """Convert string value to JSON"""
        if isinstance(value, basestring):
            try:
                return json.loads(value, **self.load_kwargs)
            except ValueError:
                pass
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        """Convert JSON object to a string"""
        if isinstance(value, basestring):
            return value
        return json.dumps(value, **self.dump_kwargs)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

    def value_from_object(self, obj):
        return json.dumps(super(JSONCodeMirrorField, self).value_from_object(obj), indent=4)

    def formfield(self, **kwargs):
        if "form_class" not in kwargs:
            kwargs["form_class"] = JSONFormField

        # kwargs["widget"] = CodeMirrorJSONWidget()
        kwargs["widget"] = CodeMirrorUploadWidget()

        field = super(JSONCodeMirrorField, self).formfield(**kwargs)

        if not field.help_text:
            field.help_text = "Enter valid JSON"

        return field

import yaml


class YAMLFormField(Field):
    # widget = CodeMirrorJSONWidget
    
    def clean(self, value):
        if not value and not self.required:
            return None
        value = super(YAMLFormField, self).clean(value)
        
        try:
            yaml.load(value)
        except ValueError:
            raise FormValidationError(_("Enter valid YAML"))
        print type(value)
        return value


class YAMLCodeMirrorField(models.TextField):
    __metaclass__ = models.SubfieldBase

    def to_python(self, value):
        # if isinstance(value, basestring):
        #     try:
        #         return yaml.load(value)
        #     except ValueError:
        #         pass
        return value

    def get_db_prep_value(self, value, connection, prepared=False):
        if isinstance(value, basestring):
            return value
        return value # yaml.dump(value, default_flow_style=False)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return value

    def value_from_object(self, obj):
        val = super(YAMLCodeMirrorField, self).value_from_object(obj)
        return val #yaml.dump(val, default_flow_style=False)

    def formfield(self, **kwargs):
        if "form_class" not in kwargs:
            kwargs["form_class"] = YAMLFormField

        kwargs["widget"] = YAMLCodeMirrorAJAXUploadWidget()

        field = super(YAMLCodeMirrorField, self).formfield(**kwargs)

        if not field.help_text:
            field.help_text = "Enter valid YAML"

        return field

    def contribute_to_class(self, cls, name):
        super(YAMLCodeMirrorField, self).contribute_to_class(cls, name)
        def as_python(self):
            value = getattr(self, name)
            try:
                return yaml.load(value)
            except ValueError:
                pass
        cls.add_to_class('{0}_as_python'.format(name), as_python)

"""
I need the field to... coerce to python normally
BUT, on database save, I need the form input to go to the database verbatim.

Not coerced to python, then converted to a string.
"""


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([], ["^codemirror\.fields\.JSONCodeMirrorField"])
except:
    pass