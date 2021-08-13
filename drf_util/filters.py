from django_filters.rest_framework import DjangoFilterBackend


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
