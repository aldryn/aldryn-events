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
        try:
            # If django_tablib is available, use it.
            # This logic is here, because the official version of
            # django-tablib currently does not support Django 1.9.
            # So we can't install it by default from setup.py.
            # On aldryn the aldryn-django Addon will install the appropriate
            # patched version of django-tablib, so it should be available.
            # Once django-tablib works with all required Django versions again
            # this logic can be removed and django-tablib can be added to
            # setup.py again.
            import django_tablib
            settings['INSTALLED_APPS'].append('django_tablib')
        except ImportError:
            pass
        return settings
