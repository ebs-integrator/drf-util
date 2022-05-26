from rest_framework import serializers
from drf_util.serializers import build_model_serializer
from tests.models import Thing, AnotherThing


class ThingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thing
        fields = '__all__'


AnotherThingSerializer = build_model_serializer(
    things=ThingSerializer(many=True),
    meta_model=AnotherThing,
)
