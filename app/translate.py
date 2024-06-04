import requests
from flask_babel import _ 
from flask import current_app


def translate(text, source_language, dest_language):
    print('inside')
    if 'MS_TRANSLATOR_KEY' not in current_app.config or \
        not current_app.config['MS_TRANSLATOR_KEY']:
        return _('Error: the translation service is not configured')
    auth = {
        'Ocp-Apim-Subscription-Key': current_app.config['MS_TRANSLATOR_KEY'],
        'Ocp-Apim-Subscription-Region': 'uksouth',
    }

    r = requests.post(
        'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from={}&to={}'.format(
            source_language, dest_language), headers=auth, json=[{'Text': text}]
    )

    if r.status_code!=200:
        return _('Failed: The translation service did not work!!')
    print(r, '\n', r.json())
    return r.json()[0]['translations'][0]['text']