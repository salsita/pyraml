"""RAML (REST API Markup Language) enhanced loader."""

__all__ = 'Loader'.split()

import dataloader

class Loader(dataloader.Loader):
    default_markup = 'raml'

    name = 'api spec'

    def postprocess(self, spec, name=None, uri=None, params=None):
        spec['id'] = '{title} {version}'.format(**spec).lower().replace(' ', '_')
        spec['api'] = {}

        if uri is None:
            from urlparse import urlparse
            uri = urlparse(spec.get('baseUri', '')).path

        if params is None:
            params = spec.get('baseUriParameters', None)

        spec['allUriParameters'] = params = dict(
            (key, param) for key, param in params.items() if '{{{0}}}'.format(key) in uri) if params else {}
        spec['uri'] = spec['relativeUri'] = uri

        for resource in spec['resources']:
            resource['allUriParameters'] = dict(params)
            self.postprocess_resource(spec, uri, resource)

        if self.log:
            self.log.info('got %s: %s resources', name or self.name, len(spec['api']))

        return spec

    def postprocess_resource(self, spec, uri, resource):
        uri += self.get_resource_uri(resource)
        spec['api'][uri] = resource
        resource['uri'] = uri
        resource['methodsByName'] = methods_by_name = {}

        if self.log:
            self.log.debug('add %s %s %s', spec['id'], '/'.join(m['method'].upper() for m in resource.get('methods', [])) or '-', uri)

        for method in resource.setdefault('methods', []):
            methods_by_name[method['method']] = method
            method['uri'] = uri
            method['allUriParameters'] = resource['allUriParameters']
            for status, response in method.setdefault('responses', {}).items():
                if not response:
                    method['responses'][status] = response = {}

                response['status'] = int(status)

                for mimetype, body in response.setdefault('body', {}).items():
                    if not body:
                        response['body'][mimetype] = body = {}

                    body['mimetype'] = mimetype

        for sub_resource in resource.get('resources', ()):
            sub_resource['allUriParameters'] = dict(resource['allUriParameters'])
            self.postprocess_resource(spec, uri, sub_resource)

    def get_resource_uri(self, resource):
        return resource['relativeUri']
