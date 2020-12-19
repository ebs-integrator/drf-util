from rest_framework.fields import Field, empty
from rest_framework.serializers import Serializer

from elasticsearch_dsl.search import Search

from .fields import DslField


__all__ = [
    'DslSerializer',
]


class DslSerializer(Serializer):
    def create(self, validated_data):
        class_name = self.__class__.__name__
        raise RuntimeError(f'Instance of {class_name} has not model attached.')

    def update(self, instance, validated_data):
        class_name = self.__class__.__name__
        raise RuntimeError(f'Instance of {class_name} has not model attached.')

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
