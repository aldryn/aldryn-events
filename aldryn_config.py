from aldryn_client import forms


class Form(forms.BaseForm):
    plugin_styles = forms.CharField('List of additional plugin styles (comma separated)', required=False)

    def to_settings(self, data, settings):
        settings['ALDRYN_EVENTS_PLUGIN_STYLES'] = data['plugin_styles']
        return settings
