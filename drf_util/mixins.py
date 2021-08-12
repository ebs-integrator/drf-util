from collections import OrderedDict

from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.inspectors import SwaggerAutoSchema
from drf_yasg.inspectors.base import call_view_method
from drf_yasg.utils import guess_response_status, no_body


class CustomAutoSchema(SwaggerAutoSchema):
    def get_view_response_serializer(self):
        return call_view_method(self.view, 'get_serializer')

    def get_view_serializer(self):
        return call_view_method(self.view, 'get_serializer_create')

    def get_view_query_serializer(self):
        return call_view_method(self.view, 'get_query_serializer')

    def get_default_response_serializer(self):
        body_override = self._get_request_body_override()
        if body_override and body_override is not no_body:
            return body_override

        return self.get_view_response_serializer()

    def get_query_serializer(self):
        if self.overrides.get('query_serializer', None) is None:
            self.overrides['query_serializer'] = self.get_view_query_serializer()
        return super(CustomAutoSchema, self).get_query_serializer()

    def get_default_responses(self):
        """Get the default responses determined for this view from the request serializer and request method.

        :type: dict[str, openapi.Schema]
        """
        method = self.method.lower()

        default_status = guess_response_status(method)
        default_schema = ''
        if method in ('get', 'post', 'put', 'patch'):
            default_schema = self.get_default_response_serializer()

        default_schema = default_schema or ''
        if default_schema and not isinstance(default_schema, openapi.Schema):
            default_schema = self.serializer_to_schema(default_schema) or ''  # noqa

        if default_schema:
            if self.has_list_response():
                default_schema = openapi.Schema(type=openapi.TYPE_ARRAY, items=default_schema)
            if self.should_page():
                default_schema = self.get_paginated_response(default_schema) or default_schema

        return OrderedDict({str(default_status): default_schema})


class BothHttpAndHttpsSchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request, public)
        schema.schemes = ["http", "https"]
        return schema
