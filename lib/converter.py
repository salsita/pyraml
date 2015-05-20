"""RAML (REST API Markup Language) parameter converter."""

__all__ = 'Converter ParameterError'.split()

import re
from datetime import datetime, timedelta
from email.utils import parsedate_tz, mktime_tz

from errors import ParameterError

class Converter(object):
    class RAML(object):
        epoch = datetime(1970, 1, 1)
        bools = dict(
            true = True,
            false = False,
            )

        @classmethod
        def parse_bool(cls, text):
            return cls.bools[text]

        @classmethod
        def parse_date(cls, text):
            return epoch + timedelta(seconds=mktime_tz(parsedate_tz(text)))

    converters_per_type = dict(
        integer = int,
        number = float,
        string = unicode,
        boolean = RAML.parse_bool,
        date = RAML.parse_date,
        )

    log = None
    ignore_empty_params = True

    def convert_params(self, specification, params):
        converted = {}
        for name, spec in specification.items():
            value = params.get(name, None)

            if value is None or value == '' and self.ignore_empty_params and '' not in spec.get('enum', ()):
                if spec.get('required', False):
                    raise ParameterError(name, '{missing} required parameter: {name!r}',
                        missing = 'misssing' if value is None else 'empty')

                value = spec.get('default', None)

                if value is None:
                    converted[name] = None
                    continue

            converted[name] = self.convert_param(name, spec, value)

        return converted

    def convert_param(self, name, spec, value):
        try:
            return self.validate(name, spec, self.convert(name, spec, value))
        except (TypeError, ValueError) as error:
            if self.log:
                self.log.exception('ParameterError: %s: %s: %r', name, error, value)
            raise ParameterError(name, '{name}: {error}', error=error)

    def convert(self, name, spec, value):
        return self.converters_per_type[spec['type']](value)

    def validate(self, name, spec, value):
        typename = spec['type']

        if typename == 'string' and isinstance(value, basestring):
            if 'enum' in spec and value not in spec['enum']:
                raise ValueError('not one of {0!r}: {1!r}'.format(spec['enum'], value))

            if 'pattern' in spec:
                pattern = spec['pattern']
                if isinstance(pattern, basestring):
                    pattern = spec['pattern'] = re.compile(pattern)
                if not pattern.search(value):
                    raise ValueError('does not match regexp {0!r}: {1!r}'.format(pattern.pattern, value))

            if 'minLength' in spec and len(value) < spec['minLength']:
                raise ValueError('too short: {0} < {1!r}'.format(len(value), spec['minLength']))

            if 'maxLength' in spec and len(value) > spec['maxLength']:
                raise ValueError('too long: {0} > {1!r}'.format(len(value), spec['maxLength']))

        elif typename in ('integer', 'number'):
            if 'minimum' in spec and value < spec['minimum']:
                raise ValueError('too small: {0!r} < {1!r}'.format(value, spec['minimum']))

            if 'maximum' in spec and value > spec['maximum']:
                raise ValueError('too large: {0!r} > {1!r}'.format(value, spec['maximum']))

        return value

    def __str__(self):
        return '{0}.{1}({2})'.format(self.__class__.__module__, self.__class__.__name__.lower(),
            ', '.join(k.replace('converters_', '') for k in dir(self) if k.startswith('converters_')))
