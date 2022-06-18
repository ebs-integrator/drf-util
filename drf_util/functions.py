from django.contrib.postgres.fields import ArrayField
from django.db import models


class StringToArr(models.Func):  # noqa
    function = 'STRING_TO_ARRAY'
    lookup_name = 'to_arr'
    template = '%(function)s(%(expressions)s)'

    def __init__(self, field, separator, *args, **kwargs):
        super().__init__(field, separator, *args, **kwargs)


class ArrIntersection(models.Func):  # noqa
    function = 'array'
    lookup_name = 'to_arr'
    template = '%(function)s(select unnest(%(first_array)s) intersect all select unnest(%(second_array)s))'
    _output_field_resolved_to_none = ArrayField(models.CharField(max_length=200))

    def __init__(self, first_array, second_array, *args, **kwargs):
        super().__init__(first_array, second_array, *args, **kwargs)

    def as_sql(self, compiler, connection, template=None, **extra_context):
        first_array, second_array = self.source_expressions
        first_array_sql, first_array_params = compiler.compile(first_array)
        second_array_sql, second_array_params = compiler.compile(second_array)
        extra_context = {
            **extra_context,
            'first_array': first_array_sql,
            'second_array': second_array_sql,
        }
        return super().as_sql(compiler, connection, template, **extra_context)


class ArrayLength(models.Func):  # noqa
    function = 'CARDINALITY'
