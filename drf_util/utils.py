import glob
import sys
from typing import Any

from dateutil import parser
from django.conf import settings
from django.db.models import QuerySet, ForeignKey, ManyToManyField
from django.db.models import TextChoices
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.serializers import Serializer

from drf_util.mixins import BothHttpAndHttpsSchemaGenerator


class Colors(TextChoices):
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def dict_merge(a, b, path=None):
    if path is None:
        path = []

    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                dict_merge(a[key], b[key], path + [str(key)])
            elif a[key] == b[key]:
                pass  # same leaf value
            else:
                pass
                # a[key] = b[key]
                # raise Exception('Conflict at %s' % '.'.join(path + [str(key)]))
        else:
            a[key] = b[key]

    return a


def gt(obj: object, path: str, default: Any = None, sep: str = '.') -> Any:
    """
    Function that extracts the value from the specified path in obj and returns default if nothing found
    :param obj: Parameter in which we are searching for values in
    :param path: Path we are trying to search for in our obj
    :param default: Default value we return if nothing found in that path
    :param sep: Separator used between path values
    :return: Value in obj path if it exists or default value
    """

    def _dispatch_item(_obj, _key):
        if _key == '*':
            for item in _obj:
                yield item

        elif hasattr(_obj, '__getitem__'):
            if _key.isdigit():
                yield _obj.__getitem__(int(_key))
            else:
                yield _obj.__getitem__(_key)

        else:
            yield getattr(_obj, _key)

    def _dispatch_list(_gen, _key):
        for _obj in _gen:
            for item in _dispatch_item(_obj, _key):
                yield item

    obj = [obj]

    for key in path.split(sep):
        obj = _dispatch_list(obj, key)

    try:
        obj = list(obj)
    except Exception:
        return default

    if len(obj) <= 1:
        obj = next(iter(obj), default)

    return obj


def sf(function, exception=Exception):
    try:
        return function()
    except exception:
        pass


def join_url(part_one: str, part_two: str):
    return '/'.join([part_one.rstrip('/'), part_two.lstrip('/')])


def st(path, value):
    dict_return = {}
    parts = path.split('.')
    if not path:
        return value
    key = parts.pop(0)
    dict_return[key] = st(".".join(parts), value)
    return dict_return


def get_object_labels(obj, names=None):
    labels = []
    iterate = []

    if isinstance(obj, dict):
        iterate = obj.items()
    elif isinstance(obj, list):
        iterate = enumerate(obj)

    for key, value in iterate:
        if isinstance(value, str):
            if names:
                if key in names:
                    labels.append(value)
            else:
                labels.append(value)
        else:
            labels = labels + get_object_labels(value, names)

    return list(set(labels))


def fetch_objects(instance, function, select=50):
    skip = 0
    while True:
        objects = list(instance[skip:skip + select])

        if len(objects) == 0:
            break

        skip += select

        for obj in objects:
            function(obj)


def offset_objects(key, get_function, save_function, storage):
    offset = storage.get(key)
    while True:
        objects, offset = get_function(offset)
        if not objects:
            break

        for object_data in objects:
            save_function(object_data['ocid'])

        storage.put(key, offset)


def date(item):
    try:
        return parser.parse(item, ignoretz=not getattr(settings, 'USE_TZ', False))
    except TypeError:
        return None


def to_dt(items):
    for k, item in enumerate(items):
        if item:
            items[k] = parser.parse(item, ignoretz=not getattr(settings, 'USE_TZ', False))

    return items


def min_next(items, min_value=None):
    for item in sorted(filter(lambda x: x is not None, items)):
        if min_value < item:
            return item

    return None


def any_value(items: list):
    """
    Function that extracts values from a list and checks if they are diff from None,0,{},[],False...
    First value that is diff from them is being returned
    :param items: List of items that is searched for non-null values
    :return: First value that fits the criteria
    """
    for item in items:
        if item:
            return item


def iterate_query(queryset, offset_field, offset_start, limit=100):
    while True:
        object_list = list(queryset.filter(**{offset_field + "__gt": offset_start}).order_by(offset_field)[:limit])
        if not len(object_list):
            break

        for obj in object_list:
            offset_start = getattr(obj, offset_field)
            yield obj


def get_applications(base_folder=gt(settings, 'APPS_PATH', 'apps'), inside_file='', only_directory=True):
    if inside_file:
        inside_file += '*'

    separator = '\\' if sys.platform.startswith('win') else '/'

    apps = [
        '.'.join(directory.split(separator)[:-1 if only_directory else None]).replace('.py', '')
        for directory in glob.glob(f"{base_folder}/[!_]*/{inside_file}", recursive=True)
    ]
    return apps


def add_related(queryset, serializer) -> QuerySet:
    select_related = []
    prefetch_related = []

    if not isinstance(serializer, Serializer):
        serializer = serializer()

    for field_name, field_data in serializer.fields.items():
        field_name = getattr(field_data, 'source', field_data)
        field = gt(queryset.model, field_data.source, None)
        if not field or not hasattr(field, 'field'):
            continue

        if isinstance(field.field, (ForeignKey, ManyToManyField)):
            if hasattr(field, 'rel'):
                prefetch_related.append(field_name)
            else:
                select_related.append(field_name)

    return queryset.select_related(*select_related).prefetch_related(*prefetch_related)


def get_custom_schema_view(title, default_version='v1', description='', *args, **kwargs):
    return get_schema_view(
        info=openapi.Info(
            title=title,
            default_version=default_version,
            description=description,
        ),
        validators=['ssv'],
        generator_class=BothHttpAndHttpsSchemaGenerator,
        public=True,
        permission_classes=(AllowAny,),
        *args,
        **kwargs
    )
