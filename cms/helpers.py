from django.conf import settings

def get_language(language_code):
    '''
    returns language name
    '''
    for code, name in settings.LANGUAGES:
        if language_code == code:
            return name
    else:
        return None
