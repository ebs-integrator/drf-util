from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters


class CustomFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):  # noqa
        filterset_class = getattr(view, 'filterset_class', None)  # noqa
        filterset_fields = getattr(view, 'filterset_fields', None)  # noqa

        if filterset_class is None and hasattr(view, 'filter_class'):
            filter_class = getattr(view, 'filter_class', None)
            if type(filter_class) is dict and view.action in filter_class:
                filterset_class = filter_class[view.action]  # noqa
            elif type(filter_class) is not dict:
                filterset_class = getattr(view, 'filter_class', None)  # noqa

        if filterset_fields is None and hasattr(view, 'filter_fields'):
            filterset_fields = getattr(view, 'filter_fields', None)  # noqa

        if filterset_class:
            filterset_model = filterset_class._meta.model  # noqa

            # FilterSets do not need to specify a Meta class
            if filterset_model and queryset is not None:
                if not issubclass(queryset.model, filterset_model):
                    return 'FilterSet model %s does not match queryset model %s' % \
                           (filterset_model, queryset.model)

            return filterset_class

    def field_to_schema(self, field):
        import coreschema
        import django.forms as django_forms
        from django.utils.encoding import force_str
        title = force_str(field.label) if field.label else ''
        description = force_str(field.help_text) if field.help_text else ''

        schema = None

        if isinstance(field, django_forms.MultipleChoiceField):
            schema = coreschema.Array(
                items=coreschema.Enum(enum=list(field.choices)),
                title=title,
                description=description
            )
        elif isinstance(field, django_forms.ChoiceField) and not isinstance(field, django_forms.ModelChoiceField):
            choices = list(map(lambda choice: choice[0] if isinstance(choice, tuple) else choice, field.choices))
            choices.remove('')
            schema = coreschema.Enum(
                enum=choices,
                title=title,
                description=description
            )
        elif isinstance(field, django_forms.BooleanField):
            schema = coreschema.Boolean(title=title, description=description)
        elif isinstance(field, (django_forms.DecimalField, django_forms.FloatField)):
            schema = coreschema.Number(title=title, description=description)
        elif isinstance(field, django_forms.IntegerField):
            schema = coreschema.Integer(title=title, description=description)
        elif isinstance(field, django_forms.DateField):
            schema = coreschema.String(
                title=title,
                description=description,
                format='date'
            )
        elif isinstance(field, django_forms.DateTimeField):
            schema = coreschema.String(
                title=title,
                description=description,
                format='date-time'
            )
        elif isinstance(field, django_forms.JSONField):
            schema = coreschema.Object(title=title, description=description)

        return schema or coreschema.String(title=title, description=description)

    def get_coreschema_field(self, field):
        return self.field_to_schema(field.field)


class CustomOrderingFilter(filters.OrderingFilter):

    def get_schema_fields(self, view):
        from rest_framework.compat import coreapi, coreschema
        from django.utils.encoding import force_str

        assert coreapi is not None, 'coreapi must be installed to use `get_schema_fields()`'
        assert coreschema is not None, 'coreschema must be installed to use `get_schema_fields()`'
        schema = coreschema.String(
            title=force_str(self.ordering_title),
            description=force_str(self.ordering_description),
        )

        ordering_fields = getattr(view, 'ordering_fields', None)
        if ordering_fields and ordering_fields != '__all__':
            negative_fields = [f'-{field}' for field in ordering_fields if not field.startswith('-')]
            schema = coreschema.Enum(
                title=force_str(self.ordering_title),
                description=force_str(self.ordering_description),
                enum=sorted({*ordering_fields, *negative_fields})
            )

        return [
            coreapi.Field(
                name=self.ordering_param,
                required=False,
                location='query',
                schema=schema
            )
        ]
