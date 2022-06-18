from drf_util.views import BaseModelViewSet
from tests.models import Thing
from tests.serializers import ThingSerializer


class ThingViewSet(BaseModelViewSet):
    queryset = Thing.objects.all()
    serializer_class = ThingSerializer
    filterset_fields = ['title', 'another_thing']
    search_fields = filterset_fields
    ordering_fields = filterset_fields
    ordering = filterset_fields


class ThingRelatedViewSet(BaseModelViewSet):
    queryset = Thing.objects.all()
    serializer_class = ThingSerializer
    filterset_fields = ['title', 'another_thing']
    search_fields = filterset_fields
    ordering_fields = filterset_fields
    ordering = filterset_fields
    autocomplete_related = False
    select_related = (
        'another_thing'
    )
    prefetch_related = (
        'other_things',
        'other_things__another_thing'
    )
