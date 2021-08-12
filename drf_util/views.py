import warnings

from django.db.models import QuerySet
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, filters, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf_util.filters import CustomFilterBackend
from drf_util.pagination import CustomPagination
from drf_util.utils import add_related

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
    serializer_by_action = {}
    permission_classes_by_action = {"default": [IsAuthenticated]}
    autocomplete_field = None

    def get_queryset(self) -> QuerySet:
        queryset = super().get_queryset()
        if self.serializer_class and callable(self.get_serializer_class()):
            queryset = add_related(queryset, self.get_serializer())
        return queryset

    def get_serializer_class(self):
        if self.action in self.serializer_by_action:
            return self.serializer_by_action[self.action]

        return super().get_serializer_class()

    def get_permissions(self):
        try:
            # return permission_classes depending on `action`
            return [permission() for permission in self.permission_classes_by_action[self.action]]
        except KeyError:
            # action is not set return default permission_classes
            default = self.permission_classes_by_action.get('default')
            if default:
                if hasattr(default, '__iter__'):
                    return [permission() for permission in default]
                else:
                    return [default()]  # noqa

            return [permission() for permission in self.permission_classes]

    def get_serializer_create(self, *args, **kwargs):
        serializer_class = self.get_serializer_create_class()
        kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get_query_serializer(self):
        if self.action == ['retrieve', 'post', 'patch']:
            return None
        return self.query_serializer

    def get_serializer_create_class(self):
        return self.serializer_create_class if self.serializer_create_class is not None else self.serializer_class

    def get_object_id(self):
        return self.kwargs.get(self.lookup_field)


class BaseListModelMixin(mixins.ListModelMixin):
    filter_backends = (filters.OrderingFilter, CustomFilterBackend, filters.SearchFilter,)
    pagination_class = CustomPagination
    filter_class = None
    search_fields = ()
    ordering_fields = '__all__'
    ordering = ['-id']


class BaseReadOnlyViewSet(BaseListModelMixin, mixins.RetrieveModelMixin, BaseViewSet):
    pass


class BaseModelItemViewSet(
    mixins.RetrieveModelMixin,
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
