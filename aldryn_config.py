from aldryn_client import forms


class Form(forms.BaseForm):
    plugin_styles = forms.CharField(
        'List of additional plugin styles (comma separated)', required=False)

    def to_settings(self, data, settings):
        choices = []
        for style in data['plugin_styles'].split(','):
            style = style.strip()
            choices.append((style, style))
        settings['ALDRYN_EVENTS_PLUGIN_STYLES'] = choices
        settings['INSTALLED_APPS'].append('django_tablib')
        return settings
