"""
CodeMirror 2 Django Widgets
---------------------------

Created on Thursday, April 2012 by Yuji Tomita
"""
import json

from django import forms
from django.utils.safestring import mark_safe


""" 
Alex Martelli recursive dict update
http://stackoverflow.com/questions/3232943/update-value-of-a-nested-dictionary-of-varying-depth
"""
import collections

def recursive_update(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = recursive_update(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d


def _create_widget(*args, **kwargs):
    """
    Dynamically creates a Widget class
    - Put here due todynamic Meta class.
    """
    extra_css = kwargs.pop('css', {})
    extra_js = kwargs.pop('js', [])
    default_options = kwargs.pop('options', {})

    class CodeMirrorWidget(forms.Textarea):
        class Media:
            css = {
                'all': [
                    'codemirror/lib/codemirror.css',
                    'codemirror/theme/monokai.css',
                    ] + extra_css
            }

            js = [
                'codemirror/lib/codemirror.js', 
            ] + extra_js
            # staticfiles automatically prepends static storage

        def __init__(self, *args, **kwargs):
            self.new_options = kwargs.pop('options', {})
            super(CodeMirrorWidget, self).__init__(*args, **kwargs)
        
        def render(self, name, value, attrs=None):
            u"""Render CodeMirrorTextarea"""
            html = super(CodeMirrorWidget, self).render(name, value, attrs)
            options = {
                'mode': {
                    'name': "python",
                    'version': 2,
                    'singleLineStringErrors': False,
                    },
                'lineNumbers': True,
                'indentUnit': 4,
                'tabMode': "shift",
                'matchBrackets': True,
                'theme': 'monokai',
            }
            recursive_update(options, default_options)
            recursive_update(options, self.new_options)
            # myCodeMirror.replaceSelection('foobar');
            output = u'''{html}
            <script type="text/javascript">
                var myCodeMirror = CodeMirror.fromTextArea(document.getElementById("{id}"), {options});
                $("#{id}").data('codemirror', myCodeMirror);
            </script> 
            '''.format(
                id=attrs['id'],
                html=html,
                options=json.dumps(options),
                )
            return mark_safe(output)
    return CodeMirrorWidget


CodeMirrorPythonWidget = _create_widget(
    css=['codemirror/theme/monokai.css'],
    js=['codemirror/mode/python/python.js'],
    )


CodeMirrorJSONWidget = _create_widget(
    options={
        "mode": {
            'name': 'javascript',
            'json': True
        }
    },
    css=['codemirror/theme/monokai.css'],
    js=['codemirror/mode/javascript/javascript.js'],
    )