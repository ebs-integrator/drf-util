from dateutil import parser
from django.db.models.base import Model


def gt(obj, path, default=None):
    try:
        parts = path.split('.')

        for part in parts:
            if part.isdigit():
                obj = obj[int(part)]
            elif isinstance(obj, Model):
                obj = getattr(obj, part, default)
            else:
                obj = obj.get(part, default)

        return obj

    except Exception:
        return default


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
            labels = labels + get_object_labels(value)

    return labels


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
        return parser.parse(item)
    except TypeError:
        return None


def to_dt(items):
    for k, item in enumerate(items):
        if item:
            items[k] = parser.parse(item)

    return items


def min_next(items, min_value=None):
    for item in sorted(filter(lambda x: x is not None, items)):
        if min_value < item:
            return item

    return None


def any_value(items: list):
    for item in items:
        if item:
            return item
