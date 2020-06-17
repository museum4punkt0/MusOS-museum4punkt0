'''
math utilities

:author: Jens Gruschel
:copyright: © 2019 contexagon GmbH

:license: This file is part of MusOS and is released under the GPLv3 license.
          Please see the LICENSE.md file that should have been included
          as part of this package.

'''


def get_int_or_default(value, default_value = 0):

    try:
        return int(value)
    except:
        return default_value


def get_float_or_default(value, default_value = 0.0):

    try:
        return float(value)
    except:
        return default_value
