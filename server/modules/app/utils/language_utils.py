'''
multi language text translation utilities

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


def translate(value, language = 'de'):
    if isinstance(value, str):
        return value
    elif isinstance(value, dict):
        result = dict.get(language) or dict.get('en') or dict.get('de')
        return result if isinstance(result, str) else None
    else:
        return None