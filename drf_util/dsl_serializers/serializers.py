from typing import Type
from datetime import datetime, time

from rest_framework.fields import empty, IntegerField, FloatField, DateTimeField, DateField, TimeField
from rest_framework.serializers import Serializer

from elasticsearch_dsl.query import Query, Range
from elasticsearch_dsl.search import Search

from .fields import DslField, DslQueryField


__all__ = [
    'DslSerializer', 'DslQuerySerializer',
    'IntegerRangeQueryField', 'FloatRangeQueryField',
    'DateTimeRangeQueryField', 'DateRangeQueryField',
]


class DslSerializer(Serializer):
    def create(self, validated_data):
        raise RuntimeError()

    def update(self, instance, validated_data):
        raise RuntimeError()

    def get_search(self, search=None, *args, **kwargs) -> Search:
        values = self.validated_data
        fields = self.fields

        search = search or Search()
        if not isinstance(search, Search):
            raise ValueError(f"Argument 'search' expected instance of Search but got {search}")

        for name, field in fields.items():
            if not isinstance(field, DslField):
                continue

            value = field.get_value(values)
            if value is empty:
                continue

            search = field.get_search(value, search, *args, **kwargs)

        return search


class DslQuerySerializer(Serializer, DslQueryField):
    dsl_query: Type[Query]
    doc_field: str

    def create(self, validated_data):
        raise RuntimeError()

    def update(self, instance, validated_data):
        raise RuntimeError()


class IntegerRangeQueryField(DslQuerySerializer):
    dsl_query = Range

    gt = IntegerField(required=False)
    lt = IntegerField(required=False)
    gte = IntegerField(required=False)
    lte = IntegerField(required=False)


class FloatRangeQueryField(DslQuerySerializer):
    dsl_query = Range

    gt = FloatField(required=False)
    lt = FloatField(required=False)
    gte = FloatField(required=False)
    lte = FloatField(required=False)


class DateTimeRangeQueryField(DslQuerySerializer):
    dsl_query = Range

    gt = DateTimeField(required=False)
    lt = DateTimeField(required=False)
    gte = DateTimeField(required=False)
    lte = DateTimeField(required=False)


class DateRangeQueryField(DslQuerySerializer):
    dsl_query = Range

    gt = DateField(required=False)
    lt = DateField(required=False)
    gte = DateField(required=False)
    lte = DateField(required=False)

    def to_internal_value(self, data):
        value = super(DateRangeQueryField, self).to_internal_value(data)

        if 'gt' in value:
            value['gt'] = datetime.combine(date=value['gt'], time=time.min)
        if 'lt' in value:
            value['lt'] = datetime.combine(date=value['lt'], time=time.max)
        if 'gte' in value:
            value['gte'] = datetime.combine(date=value['gte'], time=time.min)
        if 'lte' in value:
            value['lte'] = datetime.combine(date=value['lte'], time=time.max)

        return value
