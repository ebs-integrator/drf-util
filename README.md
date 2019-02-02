# Django Rest Framework - Utils

A set of util functions used in EBS Projects

### Install:
```bash
pip install git+https://git2.devebs.net/ebs-platform/drf-base.git
```

### Packages

#### Functions 

- gt(obj, path, default=None)
```
>>> data = {"a":{"b": 1}}
>>> print(gt(data, 'a.b'))
1
```

- get_object_labels(obj, path, default=None)
```
>>> data = {"a":{"b": 'title'}, "c": 'test'}
>>> print(get_object_labels(data))
['title', 'test']


>>> data = {"a":{"b": 'title'}, "c": 'test'}
>>> print(get_object_labels(data, ['c']))
['test']
```

#### Decorators

```
@serialize_decorator(OrderEmployeeSerializer)
```

#### Managers

- NoDeleteManager

#### Models

- CommonModel - with date_created and date_updated
- NoDeleteModel - with date_deleted
- AbstractJsonModel - with languages

#### Validators

- ObjectExistValidator
- ObjectUniqueValidator
- PhoneValidator