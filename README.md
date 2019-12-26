# Django Rest Framework - Utils

A set of util functions used in EBS Projects

### Install:
```bash
pip install drf_util
```

### Functions

#### Get value from an object by path

Definition:

```python
gt(obj, path, default=None,sep='.')
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

- ObjectExistValidator - check if object exists
- ObjectUniqueValidator - check if object not exists
- PhoneValidator - check phone

### Serializers

#### ElasticFilterSerializer - make easy conversion between serializer data and elastic filters

```python
class TenderFilterSerializer(PaginatorSerializer, ElasticFilterSerializer):
    sort_criteria = [{"date_updated": {"order": "desc"}}, "_score"]

    status = StringListField(required=False)
    date_start = serializers.DateField(required=False)
    date_end = serializers.DateField(required=False)

    def filter_status(self, value):
        return {'terms': {
            'search_status.keyword': value
        }}

    def filter_date_start(self, value):
        return {
            "range": {
                "tenderPeriod.startDate": {'gte': value}
            }
        }

    def filter_date_end(self, value):
        return {
            "range": {
                "tenderPeriod.startDate": {'lte': value}
            }
        }

class TenderListView(GenericAPIView):
    @serialize_decorator(TenderFilterSerializer)
    def get(self, request, *args, **kwargs):
        return Response(es_app.search_response(request.serializer, 'tenders_index'))
```

#### FilterSerializer - filter queryset by serializer fields

```python
class ServiceListQuerySerializer(FilterSerializer):
    name = CharField(required=False)
    tag_id = CharField(required=False)
    type = CharField(required=False)
    status = CharField(required=False)

    def filter_name(self, value, queryset):
        return queryset.filter(name__icontains=value)

    def filter_tag_id(self, value, queryset):
        return queryset.filter(tags__contains=value)

    def filter_type(self, value, queryset):
        return queryset.filter(type=value)

    def filter_status(self, value, queryset):
        return queryset.filter(status=value)


class ServiceListView(ListAPIView):
    serializer_class = ServiceListQuerySerializer

    @swagger_auto_schema(query_serializer=ServiceListQuerySerializer)
    @serialize_decorator(ServiceListQuerySerializer)
    def get(self, request):
        services = request.serializer.get_filter(request.valid, Service.objects.all())
        return Response(ServiceSerializer(instance=services, many=True).data)
```


#### ChangebleSerializer - metamorphic serializer

```python
class ContractNoticeCancelView(GenericAPIView):
    def put(self, request):
        serializer_meta = {
            'id': PrimaryKeyRelatedField(queryset=Tender.objects.all(), required=True),
            'info': {
                'rationale': CharField(required=True),
                'description': CharField(required=True),
            },
            'documents': DocumentFileSerializer(required=True, many=True)
        }
        serializer = ChangebleSerializer(data=request.data)
        serializer.update_properties(serializer_meta)
        serializer.is_valid(raise_exception=True)

        return Response({"valid": True})
```

#### PaginatorSerializer - serializer for paginating

```python
class ListUserNotification(GenericAPIView):
    @serialize_decorator(PaginatorSerializer)
    def get(self, request):
        notifications = NotificationEvent.objects.filter(user=request.user)
        return request.serializer.response(notifications, serializer=ListNotificationSerializer)
```

#### Another serializers

- StringListField - simple string list of chars
- EmptySerializer - simple empty serializer
- IdSerializer - simple id serializer