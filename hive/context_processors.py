from django.conf import settings
from django.template.loader import render_to_string

def origin(request=None):
    return {'ORIGIN': settings.ORIGIN}

def monkeypatch_registration_email_contexts():
    import registration.models

    # If render_to_string doesn't exist, something's wrong, so bail early.
    registration.models.render_to_string

    registration.models.render_to_string = render_to_string_with_origin

def render_to_string_with_origin(template_name, dictionary=None,
                                 context_instance=None):
    if dictionary is not None:
        dictionary.update(origin())
    return render_to_string(template_name, dictionary, context_instance)

monkeypatch_registration_email_contexts()
