from drf_util.views import BaseModelViewSet
from tests.models import Thing
from tests.serializers import ThingSerializer


class ThingViewSet(BaseModelViewSet):
    queryset = Thing.objects.all()
    serializer_class = ThingSerializer
