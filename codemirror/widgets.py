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
    extra_styles = kwargs.pop('extra_css_styles', '')

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
            self.extra_css_styles = kwargs.pop('extra_css_styles', '')
            self.extra_styles = kwargs.pop('extra_css_styles', '')
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
                'matchBrackets': True,
                # 'theme': 'monokai',
                'lineWrapping': True,
            }
            recursive_update(options, default_options)
            recursive_update(options, self.new_options)
            # myCodeMirror.replaceSelection('foobar');
            codemirror_reset_styles = '''
            <style>
            .CodeMirror pre, .CodeMirror div, .CodeMirror code {
                margin: 0;
                padding: 0;
                border: 0;
                outline: 0;
                font-weight: inherit;
                font-style: inherit;
                font-size: 12px;
                line-height:100%;
                font-family: inherit;
                vertical-align: baseline;
            }
            .CodeMirror {
                border: 1px solid #eee;
            }
            .CodeMirror-scroll {
                height: auto;
                overflow-y: hidden;
                overflow-x: auto;
                width: 100%;
            }
            </style>
            '''
            output = u'''{html}
            <script type="text/javascript">
                var myCodeMirror = CodeMirror.fromTextArea(document.getElementById("{id}"), {options});
                $("#{id}").data('codemirror', myCodeMirror);
            </script>
            {styles}'''.format(
                id=attrs['id'],
                html=html,
                options=json.dumps(options),
                styles=''.join([codemirror_reset_styles, self.extra_css_styles, extra_styles])
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
    css=[
        'codemirror/theme/monokai.css',
        'codemirror/mode/css/css.css',
    ],
    js=[
        'codemirror/mode/javascript/javascript.js',
        'codemirror/mode/javascript/css.css',
        ],
    )

CodeMirrorYAMLWidget = _create_widget(
    options={
        "mode": {
            'name': 'yaml',
        },
        'indentUnit': 2,
        'tabSize': 2,
    },
    css=[
        # 'codemirror/theme/monokai.css',
    ],
    js=[
        'codemirror/mode/yaml/yaml.js',
        'codemirror/lib/util/foldcode.js',
    ],
    extra_css_styles='''
    <style>
    .CodeMirror .cm-tab {
       background: #ff8367;
    }
    </style>
    '''    
    )

# custom stateless ajax upload widget
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

class AJAXUploadWidget(forms.FileInput):
    def __init__(self, *args, **kwargs):
        self.codemirror_element = kwargs.pop('codemirror_element', None)
        self.codemirror_multi_widget = kwargs.pop("codemirror_multi_widget")
        super(AJAXUploadWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs=None):
        html = super(AJAXUploadWidget, self).render(name, value, attrs)
        output = render_to_string('codemirror/ajax_upload_widget.html', {
            'input': html,
            'id': attrs['id'],
            'codemirror_element': self.codemirror_element,
            'codemirror_multi_widget': self.codemirror_multi_widget,
            });
        return mark_safe(output)


"""
We need:
1: CodeMirror Widget
2: AJAX Upload Widget
3: Combined CodeMirrorAjaxUpload Widget (auto generated from CodeMirror + ajax argument options)
"""



class CodeMirrorUploadWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """

    def __init__(self):
        self.widgets = [CodeMirrorJSONWidget(), AJAXUploadWidget(codemirror_multi_widget=True)]
        super(CodeMirrorUploadWidget, self).__init__(self.widgets)

    def decompress(self, value):
        print 'decompressing', value
        return [value] # must return list with value for each widget (i think)

    def value_from_datadict(self,data,files,name):
        """
        Return single value for form field clean()
        """
        val = self.widgets[0].value_from_datadict(data, files, name + '_%s' % '0')
        return val

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)



class YAMLCodeMirrorAJAXUploadWidget(forms.MultiWidget):
    """
    A Widget that splits datetime input into two <input type="text"> boxes.
    """

    def __init__(self):
        self.widgets = [CodeMirrorYAMLWidget(), AJAXUploadWidget(codemirror_multi_widget=True)]
        super(YAMLCodeMirrorAJAXUploadWidget, self).__init__(self.widgets)

    def decompress(self, value):
        print 'decompressing', value
        return [value] # must return list with value for each widget (i think)

    def value_from_datadict(self,data,files,name):
        """
        Return single value for form field clean()
        """
        val = self.widgets[0].value_from_datadict(data, files, name + '_%s' % '0')
        print val, type(val)
        return val

    def format_output(self, rendered_widgets):
        return u''.join(rendered_widgets)