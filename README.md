# Django Rest Framework - Utils

A set of util functions used in EBS Projects

### Install:
```bash
pip install git+https://git2.devebs.net/ebs-platform/drf-utils.git
```

### Functions

#### Get value from an object by path

Definition:

```python
gt(obj, path, default=None)
```

Usage:

```python
>>> data = {"a":{"b": 1}}
>>> print(gt(data, 'a.b'))
1
```

#### Get recursive values from a dict by keys

Definition:
```python
get_object_labels(obj, path, default=None)
```

Usage:
```python
>>> data = {"a":{"b": 'title'}, "c": 'test'}
>>> print(get_object_labels(data))
['title', 'test']


>>> data = {"a":{"b": 'title'}, "c": 'test'}
>>> print(get_object_labels(data, ['c']))
['test']
```

#### map() alternative with chunk select

Definition:
```python
fetch_objects(instance, function, select=50)
```

Usage:
```python
>>> def print_name(obj):
        print obj.name
>>>
>>> fetch_objects(UserBigList.objects.order_by('id'), print_name, 500)
```

#### Select a first true value

Definition:
```python
any_value(items: list)
```

Usage:
```python
>>> print(any_value('', None, 0, "Some text", 50000))
Some text
```

#### Recursive merge two dict

Definition:
```python
dict_merge(a, b, path=None)
```

Usage:
```python
>>> a = {'a': {'c': 1, 'd': {'x': 1}}}
>>> b = {'a': {'e': 1, 'd': {'y': 1}}}
>>> print(dict_merge(a, b))
{'a': {'c': 1, 'e': 1, 'd': {'x': 1, 'y': 1}}}
```

### Decorators

##### serialize_decorator

Definition:
```python
serialize_decorator(serializer_method, preview_function=None, read_params=False)
```

Usage:

```python
class RestoreUserPassword(GenericAPIView):
    @serialize_decorator(RestoreUserSerializer)
    def post(self, request, *args, **kwargs):
        return Response({"valid": True})
```

### Managers

- NoDeleteManager

### Models

- CommonModel - with date_created and date_updated
- NoDeleteModel - with date_deleted
- AbstractJsonModel - with languages

### Validators

- ObjectExistValidator
- ObjectUniqueValidator
- PhoneValidator