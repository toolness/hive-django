import re
from django.core.exceptions import ValidationError

PHONE_NUMBER_RE = re.compile(r'^[0-9]{3}-[0-9]{3}-[0-9]{4}$')

def is_phone_number(s):
    '''
    >>> is_phone_number('123-456-7890')
    True

    >>> is_phone_number('lol')
    False

    >>> is_phone_number('hmm123-456-7890')
    False

    >>> is_phone_number('123-456-7890o')
    False
    '''

    if PHONE_NUMBER_RE.match(s): return True
    return False

def validate_phone_number(value):
    if not is_phone_number(value):
        raise ValidationError(
            '"%s" is not a valid phone number. Valid phone numbers '
            'must be formatted as XXX-XXX-XXXX.' % value
        )
