"""RAML (REST API Markup Language) API wrapper."""

__all__ = 'API Loader Converter Content ApiError RequestError ParameterError AuthError'.split()

from functools import wraps

from errors import *
from loader import Loader
from converter import Converter

class Content(object):
    def __init__(self, content, mimetype='*/*'):
        self.content = content
        self.mimetype = mimetype
    def __len__(self):
        return len(self.content)
    def __str__(self):
        return self.content
    def __repr__(self):
        return 'content({0}, {1})'.format(self.mimetype, len(self.content))

class API(object):
    """Flask API.
    """
    Content = Content

    plugins = dict(
        loader = Loader,
        converter = Converter,
        )
    config_exclude = set('log api spec views plugins config config_exclude'.split())

    default_status = 200
    default_methods = 'get'.split()
    default_mimetype = 'application/json'

    map_method_spec = dict(
        head = 'get',
        options = 'get',
        )

    def __init__(self, path, uri=None, id=None, log=None, **options):
        self.log = log

        for key in self.plugins:
            plugin = options.pop(key, None) or self.plugins[key]()
            setattr(self, key, plugin)
            if getattr(plugin, 'log', None) is True:
                plugin.log = self.log

        if options:
            self.__dict__.update(options)

        self.spec = self.loader(path)
        self.api = self.spec['api']

        if uri is None:
            uri = self.spec['uri']
        if not uri.startswith('/'):
            raise ValueError('base uri needs to start with slash: {0}'.format(uri))

        self.uri = uri
        self.id = id or self.spec['id']

    def get_resource(self, uri):
        if not isinstance(uri, basestring):
            return uri

        if not uri.startswith(self.uri):
            if not uri.startswith('/'):
                raise ValueError('resource uri needs to start with slash: {0}'.format(uri))
            uri = self.uri + uri

        return self.api[uri]

    def get_resource_methods(self, resource, methods=None, allow_empty=False):
        if methods is None:
            methods = [m.upper() for m in self.default_methods if m in resource['methodsByName']]
            if methods or allow_empty:
                return methods

        elif methods or allow_empty:
            if isinstance(methods, basestring):
                methods = methods.upper().split()
            else:
                methods = [m.upper() for m in methods]

            for method in methods:
                if method.lower() not in resource['methodsByName']:
                    raise ValueError('unknown resource method: {0} {1}'.format(method, resource['uri']))

            return methods

        raise ValueError('requires a {0}list/string of methods, or None, not {1} {2!r}'.format(
            '' if allow_empty else 'non-empty ', type(methods), methods))

    def get_method_spec(self, resource, method=None):
        if isinstance(resource, basestring):
            if method is None and ' ' in resource:
                method, resource = resource.split(' ', 1)
            resource = self.get_resource(resource)

        try:
            return resource['methodsByName'][method.lower()]
        except KeyError:
            try:
                return resource['methodsByName'][self.map_method_spec[method.lower()]]
            except KeyError:
                raise RequestError(405, 'unsuported resource method: {} {}', method, resource['uri'])

    def get_default_status(self):
        return self.default_status

    def get_response(self, method_spec, status=None):
        if isinstance(method_spec, basestring):
            method_spec = self.get_method_spec(method_spec)

        if status is None:
            status = self.get_default_status()

        try:
            return method_spec['responses'][str(status)]
        except KeyError:
            raise RequestError(400, 'unsupported resource response status {}', status)

    def get_response_body(self, response, mimetype=None):
        if isinstance(response, basestring):
            response = self.get_response(response)

        if mimetype is None:
            mimetype = self.get_response_mimetype(response)
        try:
            return response['body'][mimetype]
        except KeyError:
            raise RequestError(415, 'unsupported media type {!r} response for status {}',
                mimetype, response['status'])

    def get_response_headers(self, response, status=None):
        if isinstance(response, basestring):
            response = self.get_response(response)

        return response.get('headers', {})

    def get_response_mimetype(self, response, accept=None):
        if isinstance(response, basestring):
            response = self.get_response(response)

        responses = response.get('body', {})

        if accept:
            for mimetype in accept:
                if mimetype in responses:
                    return mimetype
            if '*/*' in responses:
                return '*/*'

            if not '*/*' in accept:
                raise RequestError(415, 'unsupported media type response for status {}: {!r}',
                    response['status'], ','.join(accept))

        if responses:
            if self.default_mimetype in responses:
                return self.default_mimetype

            return responses.keys()[0]

        return '*/*'

    def get_example_body(self, response, mimetype=None):
        if isinstance(response, basestring):
            response = self.get_response(response)

        body = self.get_response_body(response, mimetype)
        try:
            return self.Content(body['example'], body['mimetype'])
        except KeyError:
            raise RequestError(415, 'unsupported media type {!r} example for status {}',
                mimetype or '*/*', response['status'])

    def get_example_headers(self, response):
        if isinstance(response, basestring):
            response = self.get_response(response)

        headers = self.get_response_headers(response)
        return dict((header.replace('{?}', 'example'), value['example'])
            for header, value in headers.items())

    @property
    def config(self):
        exclude = self.config_exclude
        return dict((k, getattr(self, k))
            for k in dir(self) if k not in exclude and not k.startswith('_') and not callable(getattr(self, k)))

    def __str__(self):
        return '{0}.{1}({2}: {3}: {4} resources)'.format(self.__class__.__module__, self.__class__.__name__.lower(),
            self.id, self.uri, len(self.api))

    def __repr__(self):
        return '{0}{1}'.format(self, ''.join('\n  {0} = {1}'.format(k, v) for k, v in self.config.items()))
