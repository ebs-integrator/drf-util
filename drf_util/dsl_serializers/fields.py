from abc import abstractmethod
from typing import Any, Type, Iterable

from elasticsearch_dsl.query import Query, Term, Terms
from elasticsearch_dsl.search import Search

from rest_framework.fields import (
    Field,
    BooleanField,
    NullBooleanField,
    CharField,
    EmailField,
    RegexField,
    SlugField,
    URLField,
    UUIDField,
    IPAddressField,
    IntegerField,
    FloatField,
    DecimalField,
    DateTimeField,
    DateField,
    TimeField,
    DurationField,
    ChoiceField,
    MultipleChoiceField,
    ListField,
)


__all__ = [
    'DslField', 'DslSortField', 'DslQueryField', 'DslSourceField',
    'CharSortField', 'ChoiceSortField', 'MultipleChoiceSortField', 'CharListSortField',
    'BooleanQueryField', 'NullBooleanQueryField',
    'CharQueryField', 'EmailQueryField', 'RegexQueryField', 'SlugQueryField',
    'URLQueryField', 'UUIDQueryField', 'IPAddressQueryField',
    'IntegerQueryField', 'FloatQueryField', 'DecimalQueryField',
    'DateTimeQueryField', 'DateQueryField', 'TimeQueryField', 'DurationQueryField',
    'CharListQueryField', 'IntegerListQueryField', 'FloatListQueryField',
    'CharSourceField', 'ChoiceSourceField', 'MultipleChoiceSourceField', 'CharListSourceField',
]


class DslField(Field):
    @abstractmethod
    def get_search(self, value: Any, search: Search = None, *args, **kwargs) -> Search:
        pass


class DslSortField(DslField):
    def get_keys(self, value, *args, **kwargs):
        return value

    def get_search(self, value, search=None, *args, **kwargs):
        fields = self.get_keys(value, *args, **kwargs)
        if not isinstance(fields, Iterable):
            raise ValueError(f"Method 'get_keys' expected list of string but got {fields}")

        search = search or Search()
        if not isinstance(search, Search):
            raise ValueError(f"Argument 'search' expected instance of Search but got {search}")

        return search.sort(*list(fields))


class DslQueryField(DslField):
    doc_field: str
    dsl_query: Type[Query]

    def __init__(self, doc_field=None, dsl_query=None, *args, **kwargs):
        super(DslQueryField, self).__init__(*args, **kwargs)
        self.doc_field = doc_field or self.doc_field
        self.dsl_query = dsl_query or self.dsl_query

        doc_field = doc_field or self.doc_field
        if not isinstance(doc_field, str):
            raise ValueError(f'doc_field should be instance of str but got {type(doc_field)}')

        dsl_query = dsl_query or self.dsl_query
        if not issubclass(dsl_query, Query):
            raise ValueError(f'dsl_query should be type of Query but got {dsl_query}')

    def get_query(self, value, *args, **kwargs):
        query = self.dsl_query(**{self.doc_field: value})
        return query

    def get_search(self, value, search=None, *args, **kwargs):
        query = self.get_query(value, *args, **kwargs)
        if not isinstance(query, Query):
            raise ValueError(f"Method 'get_query' expected instance of Query but got {query}")

        search = search or Search()
        if not isinstance(search, Search):
            raise ValueError(f"Argument 'search' expected instance of Search but got {search}")

        return search.query(query)


class DslSourceField(DslField):
    def get_fields(self, value, *args, **kwargs):
        return value

    def get_search(self, value, search=None, *args, **kwargs):
        fields = self.get_fields(value, *args, **kwargs)
        if not isinstance(fields, Iterable):
            raise ValueError(f"Method 'get_keys' expected list of string but got {fields}")

        search = search or Search()
        if not isinstance(search, Search):
            raise ValueError(f"Argument 'search' expected instance of Search but got {search}")

        return search.source(fields=list(fields))


# DslSortField

class CharSortField(CharField, DslSortField):
    def get_keys(self, value, *args, **kwargs):
        return [value]


class ChoiceSortField(ChoiceField, DslSortField):
    def get_keys(self, value, *args, **kwargs):
        return [value]


class MultipleChoiceSortField(MultipleChoiceField, DslSortField):
    pass


class CharListSortField(ListField, DslSortField):
    child = CharField()


# DslQueryField


class BooleanQueryField(BooleanField, DslQueryField):
    dsl_query = Term


class NullBooleanQueryField(NullBooleanField, DslQueryField):
    dsl_query = Term


class CharQueryField(CharField, DslQueryField):
    dsl_query = Term


class EmailQueryField(EmailField, DslQueryField):
    dsl_query = Term


class RegexQueryField(RegexField, DslQueryField):
    dsl_query = Term


class SlugQueryField(SlugField, DslQueryField):
    dsl_query = Term


class URLQueryField(URLField, DslQueryField):
    dsl_query = Term


class UUIDQueryField(UUIDField, DslQueryField):
    dsl_query = Term


class IPAddressQueryField(IPAddressField, DslQueryField):
    dsl_query = Term


class IntegerQueryField(IntegerField, DslQueryField):
    dsl_query = Term


class FloatQueryField(FloatField, DslQueryField):
    dsl_query = Term


class DecimalQueryField(DecimalField, DslQueryField):
    dsl_query = Term


class DateTimeQueryField(DateTimeField, DslQueryField):
    dsl_query = Term


class DateQueryField(DateField, DslQueryField):
    dsl_query = Term


class TimeQueryField(TimeField, DslQueryField):
    dsl_query = Term


class DurationQueryField(DurationField, DslQueryField):
    dsl_query = Term


class CharListQueryField(ListField, DslQueryField):
    dsl_query = Terms
    child = CharField()


class IntegerListQueryField(ListField, DslQueryField):
    dsl_query = Terms
    child = IntegerField()


class FloatListQueryField(ListField, DslQueryField):
    dsl_query = Terms
    child = FloatField()


# DslSourceField

class CharSourceField(CharField, DslSourceField):
    def get_fields(self, value, *args, **kwargs):
        return [value]


class ChoiceSourceField(ChoiceField, DslSourceField):
    def get_fields(self, value, *args, **kwargs):
        return [value]


class MultipleChoiceSourceField(MultipleChoiceField, DslSourceField):
    pass


class CharListSourceField(ListField, DslSourceField):
    child = CharField()
