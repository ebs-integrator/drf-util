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
gt(obj, path, default=None, sep='.')
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
>>> data = {"a": {"b": 'title'}, "c": 'test'}
>>> print(get_object_labels(data))
['title', 'test']

>>> data = {"a": {"b": 'title'}, "c": 'test'}
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

#### Iterate big query

Definition:

```python
iterate_query(queryset, offset_field, offset_start, limit=100)
```

Usage:

```python
queryset = Thing.objects.all()
for _ in utils.iterate_query(queryset, 'id', 0):
    ...
```

#### Get applications from folder

Definition:

```python
get_applications(base_folder='apps', inside_file='', only_directory=True)
```

Usage:

```python
# settings.py
APPS_PATH = 'path_to_aps'  # default is apps
...

# any file
get_applications()  # ['path_to_aps.app1', 'path_to_aps.app2']
get_applications(inside_file='models.py',
                 only_directory=False)  # ['path_to_aps.app1.models', 'path_to_aps.app2.models']
```

Tricks:

```python
# settings.py
INSTALLED_APPS = get_applications()
...

# urls.py
urlpatterns = [
    path("", include(application_urls))
    
    for application_urls in get_applications(
        inside_file='urls.py', only_directory=False
    ))
]
```

#### Prefetch and select related by serializer 
Definition:
```python
add_related(queryset, serializer)
```

Usage:
```python
queryset = add_related(Thing.objects.all(), ThingSerializer)
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

##### await_process_decorator

Decorator for creating a queue for using a function, it is needed to adjust the call of a function from different
processes (Сelery, Threads). For example, this decorator can be used to limit the number of requests in the parser.

Definition:

```python
# rate : count of usage some function, by default it's 20 times
# period : period of usage some function,  by default it's 1 minute
await_process_decorator(rate=20, period=60)
```

Usage:

```python
@await_process_decorator(rate=10, period=5)  # 10 times per 5 seconds 
def simple_print(text):
    print(text)
```

### Managers

- NoDeleteManager

### Models

#### BaseModel - with created_at and updated_at

```python
class Thing(BaseModel):
    title = models.CharField(max_length=20)

    class Meta:
        db_table = 'another_things'
```

- CommonModel - with date_created and date_updated
- NoDeleteModel - with date_deleted
- AbstractJsonModel - with languages

### Validators

- ObjectExistValidator - check if object exists
- ObjectUniqueValidator - check if object not exists
- PhoneValidator - check phone

### Serializers

#### BaseModelSerializer - simple serializer for BaseModel class

```python
class ThingSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Thing
```

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
- ReturnSuccessSerializer - simple success, message serializer

### Serializers functions

#### build_model_serializer - build serializer with Inheritance

Definition:
```python
build_model_serializer(base=BaseModelSerializer, add_bases=True, **kwargs)
```

Usage:
```python
ThingSerializer = build_model_serializer(
    meta_model=Thing,
)

CreateThingSerializer = build_model_serializer(
    ThingSerializer,
    meta_fields=('name', 'desctiption')
)

CreateThingSerializer = build_model_serializer(
    ThingSerializer,
    meta_fields=('name', 'desctiption')  # 'id', 'created_at' and 'updated_at' is added automatically
)

ShortThingSerializer = build_model_serializer(
    ThingSerializer,
    meta_fields=('name', 'desctiption'),
    add_bases=False  # so as not to add 'id', 'created_at' and 'updated_at'
)


AnotherThingSerializer = build_model_serializer(
    things=ThingSerializer(many=True),
    meta_model=AnotherThing,
)
```


---
**Note:**
Parameters with prefix 'meta_' is added to the meta class, the rest are added in the serializer class 
---



### Views

Note: for them to work, set in swagger settings 
DEFAULT_AUTO_SCHEMA_CLASS=drf_util.mixins.CustomAutoSchema

#### BaseModelViewSet

Usage:
```python
class ThingViewSet(BaseModelViewSet):
    queryset = Thing.objects.all()
    serializer_class = ThingSerializer
```

Attributes:

```python
queryset = None  # QuerySet

query_serializer = None  # Serializer for query
serializer_class = None  # Default and response serializer
serializer_create_class = None  # Body serializer
serializer_by_action = {}  # Serializer by action {[action]: [serializer]}

pagination_class = CustomPagination  # Pagination

filter_backends = (filters.OrderingFilter, CustomFilterBackend, filters.SearchFilter,)  # Filter backends
filter_class = None  # FilterSet
search_fields = ()  # Fields for search query_param
ordering_fields = '__all__'  # Fields for ordering query_param
ordering = ['-id']  # Default ordering fields

permission_classes_by_action = {"default": [IsAuthenticated]}  # Permission class by action {[action]: [permissions]}
```

#### Another views

- BaseViewSet
- BaseCreateModelMixin
- BaseUpdateModelMixin
- BaseListModelMixin
- BaseReadOnlyViewSet
- BaseModelItemViewSet
- BaseModelViewSet


### Pagination

#### CustomPagination

Declaration:

```python
class CustomPagination(PageNumberPagination):
    page = DEFAULT_PAGE
    page_size = 10
    page_size_query_param = 'per_page'

    def get_paginated_response(self, data):
        custom_paginator = dict(
            count=self.page.paginator.count, # noqa
            total_pages=self.page.paginator.num_pages, # noqa
            per_page=int(self.request.GET.get('per_page', self.page_size)),
            current_page=int(self.request.GET.get('page', DEFAULT_PAGE)), results=data
        )
        return Response(custom_paginator)
```

### Tests

#### CustomClient - client which check response for status code

Usage:
```python
class BaseTestCase(TestCase):
    client_class = CustomClient
    base_view = 'things'
    
    def test_list(self) -> None:
        self.client.get(reverse(f'{self.base_view}-list'))
        
    def test_duplicate(self):
        self.client.post(
            reverse(f'{self.base_view}-duplicate', args=(test_instance.pk,)),
            assert_status_code=status.HTTP_200_OK
        ).json()
```

#### BaseTestCase - test case with custom client

Usage:

```python
class ViewsTestCase(BaseTestCase, TestCase):
    def test_swagger(self):
        response = self.client.get('/swagger/?format=openapi').json()
        self.assertEqual(len(response['schemes']), 2)
```

---
**Note:**
Default setUp function authenticates the user
---

#### CRUDTestCase - test case with crud

Usage:

```python
class ThingCRUDTestCase(CRUDTestCase, TestCase):
    fixtures = ['tests/fixtures.json']
    base_view = 'things'
    queryset = Thing.objects.all()
    fake_data = {
        'title': 'Thing name'
    }
```


### Middlewares
#### PrintSQlMiddleware - middleware to print sql request and their statistics

Usage:

```python
MIDDLEWARE = [
    'drf_util.middlewares.PrintSQlMiddleware',
    ...
]
```

### Swagger utils
#### CustomAutoSchema - render schema with custom serializers methods

Usage:

```python
SWAGGER_SETTINGS = {
    'DEFAULT_AUTO_SCHEMA_CLASS': 'drf_util.mixins.CustomAutoSchema'
    ...
}
```

#### get_custom_schema_view - function to get swagger with HTTP and HTTPS

Declaration:

```python
get_custom_schema_view(title, default_version='v1', description='', *args, **kwargs)
```

Usage:

```python
schema_view = get_custom_schema_view(
    title="API Documentation",
    description="This is API Documentation"
)

urlpatterns = [
    path("", schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("redoc", schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),    
]
```




