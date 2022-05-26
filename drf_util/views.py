from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from django_filters import (
    FilterSet,
)
from drf_util.utils import add_related
from rest_framework.permissions import (
    AllowAny,
)

health_check_response = openapi.Response('Health check')


@swagger_auto_schema(methods=['get'], responses={200: health_check_response})
@api_view(['get'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'live': True})


class BaseCreateModelMixin:

    def create(self, request, return_instance=False, *args, **kwargs):
        serializer = self.get_serializer_create(data=request.data)  # noqa
        serializer.is_valid(raise_exception=True)

        instance = self.perform_create(serializer, **kwargs)

        if return_instance:
            return instance

        serializer_display = self.get_serializer(instance)  # noqa
        return Response(serializer_display.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer, **kwargs):  # noqa
        instance = serializer.save(**kwargs)
        return instance


class BaseUpdateModelMixin:

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()  # noqa
        serializer = self.get_serializer_create(instance, data=request.data, partial=partial)  # noqa
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        serializer_display = self.get_serializer(instance)  # noqa

        if getattr(instance, '_prefetched_objects_cache', None):
            instance._prefetched_objects_cache = {}

        return Response(serializer_display.data)

    def perform_update(self, serializer):  # noqa
        instance = serializer.save()
        return instance

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return self.update(request, *args, **kwargs)


class BaseViewSet(GenericViewSet):
    queryset = None
    query_serializer = None
    serializer_class = None
    serializer_create_class = None
    serializer_retrieve_class = None
    serializer_list_class = None
    serializer_by_action = {}
    permission_classes_by_action = {}
    autocomplete_field = None
    prefetch_related = ()
    select_related = ()
    autocomplete_related = True

    def get_prefetch_related(self):
        prefetch_related = self.prefetch_related
        if isinstance(prefetch_related, str) or not hasattr(prefetch_related, '__iter__'):
            prefetch_related = (prefetch_related,)

        return prefetch_related

    def get_select_related(self):
        select_related = self.select_related
        if isinstance(select_related, str) or not hasattr(select_related, '__iter__'):
            select_related = (select_related,)

        return select_related

    def get_queryset(self) -> QuerySet:
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()

        queryset = super().get_queryset()
        if self.serializer_class and callable(self.get_serializer_class()) and self.autocomplete_related:
            queryset = add_related(queryset, self.get_serializer())

        # Fetch specified relations
        if not self.autocomplete_related:
            queryset = queryset.prefetch_related(
                *self.get_prefetch_related()
            ).select_related(
                *self.get_select_related()
            )

        return queryset

    def get_serializer_by_action(self):
        return self.serializer_by_action.get(self.action)

    def get_serializer_class(self):
        return self.get_serializer_by_action() or super().get_serializer_class()

    @staticmethod
    def make_permissions(classes: list = None):
        permissions = []

        if classes is None:
            classes = []

        if not hasattr(classes, '__iter__'):
            classes = [classes]

        for permission in classes:
            permissions.append(permission() if callable(permission) else permission)

        return permissions

    def get_permissions(self):
        permissions = self.make_permissions(classes=self.permission_classes)

        try:
            # return permission_classes depending on `action`
            permissions = self.make_permissions(classes=self.permission_classes_by_action[self.action])
        except KeyError:
            # action is not set return default permission_classes_by_action, if exists
            default = self.permission_classes_by_action.get('default')
            if default:
                permissions = self.make_permissions(classes=default)

        return permissions

    def get_serializer_create(self, *args, **kwargs):
        serializer_class = self.get_serializer_create_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_retrieve(self, *args, **kwargs):
        serializer_class = self.get_serializer_retrieve_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_serializer_list(self, *args, **kwargs):
        serializer_class = self.get_serializer_list_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_query_serializer(self):
        if self.action == ['retrieve', 'post', 'patch']:
            return None
        return self.query_serializer

    def get_serializer_create_class(self):
        return self.get_serializer_by_action() or self.serializer_create_class or self.serializer_class

    def get_serializer_retrieve_class(self):
        return self.get_serializer_by_action() or self.serializer_retrieve_class or self.serializer_class

    def get_serializer_list_class(self):
        return self.get_serializer_by_action() or self.serializer_list_class or self.serializer_class

    def get_object_id(self):
        return self.kwargs.get(self.lookup_field)


class BaseListModelMixin:
    filter_class = None
    search_fields = ()
    filterset_fields = []
    ordering_fields = '__all__'
    ordering = ['-id']

    def __init__(self, **kwargs):
        # Automatically create a filter class for available filter set fields
        if not getattr(self, 'filter_class', None) and hasattr(self, 'filterset_fields'):
            # Dynamic filter classes
            namespace = self.queryset.model.__name__  # noqa
            self.filter_class = type(f'{namespace}FilterClass', (FilterSet,), {
                'Meta': type(f'{namespace}FilterMetaClass', (object,), {
                    'model': self.queryset.model,  # noqa
                    'fields': self.filterset_fields
                })
            })

        super().__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())  # noqa

        page = self.paginate_queryset(queryset)  # noqa
        if page is not None:
            serializer = self.get_serializer_list(page, many=True)  # noqa
            return self.get_paginated_response(serializer.data)  # noqa

        serializer = self.get_serializer_list(queryset, many=True)  # noqa
        return Response(serializer.data)


class BaseRetrieveModelMixin:

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()  # noqa
        serializer = self.get_serializer_retrieve(instance)  # noqa
        return Response(serializer.data)


class BaseReadOnlyViewSet(BaseListModelMixin, BaseRetrieveModelMixin, BaseViewSet):
    pass


class BaseModelItemViewSet(
    BaseRetrieveModelMixin,
    mixins.DestroyModelMixin,
    BaseCreateModelMixin,
    BaseUpdateModelMixin,
    BaseViewSet
):
    pass


class BaseModelViewSet(
    BaseListModelMixin,
    BaseModelItemViewSet
):
    pass
