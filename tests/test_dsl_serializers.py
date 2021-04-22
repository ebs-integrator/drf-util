from datetime import datetime, date, time

from elasticsearch_dsl.query import Match
from django.test import TestCase

from drf_util.dsl_serializers import (
    DslSerializer,

    CharSortField,
    ChoiceSortField,
    MultipleChoiceSortField,
    CharListSortField,
    BooleanQueryField,
    NullBooleanQueryField,
    CharQueryField,
    EmailQueryField,
    RegexQueryField,
    SlugQueryField,
    URLQueryField,
    UUIDQueryField,
    IPAddressQueryField,
    IntegerQueryField,
    FloatQueryField,
    DecimalQueryField,
    DateTimeQueryField,
    DateQueryField,
    TimeQueryField,
    CharListQueryField,
    IntegerListQueryField,
    FloatListQueryField,
    CharSourceField,
    ChoiceSourceField,
    MultipleChoiceSourceField,
    CharListSourceField,
)


class TestDslSerializer(TestCase):
    def test_serializer_a(self):
        class TestSerializer(DslSerializer):
            source = CharSourceField()
            query = CharQueryField(doc_field='doc_field')
            sort = CharSortField()

        data = {
            'source': 'doc_field',
            'query': 'value',
            'sort': 'doc_field'
        }

        serializer = TestSerializer(data=data)
        serializer.is_valid()
        search = serializer.get_search()

        expected = {
            'query': {'term': {'doc_field': 'doc_field_value'}},
            'sort': ['doc_field'],
            '_source': ['doc_field']
        }

        self.assertEqual(expected, search.to_dict())

    def test_serializer_b(self):
        class TestSerializer(DslSerializer):
            source = CharListSourceField()
            query = CharListQueryField(doc_field='doc_field')
            sort = CharListSortField()

        data = {
            'source': ['doc_field_1', 'doc_field_2'],
            'query': ['value_1', 'value_2'],
            'sort': ['doc_field_1', '-doc_field_2']
        }

        serializer = TestSerializer(data=data)
        serializer.is_valid()
        search = serializer.get_search()

        expected = {
            'query': {'terms': {'doc_field': ['value_1', 'value_2']}},
            'sort': ['doc_field_1', {'doc_field_2': {'order': 'desc'}}],
            '_source': ['doc_field_1', 'doc_field_2']
        }

        self.assertEqual(expected, search.to_dict())

    def test_serializer_c(self):
        class TestSerializer(DslSerializer):
            source = CharSourceField(required=False)
            query = CharQueryField(doc_field='doc_field', dsl_query=Match)
            sort = CharSortField(default='-date_created')

        data = {
            'query': 'value',
        }

        serializer = TestSerializer(data=data)
        serializer.is_valid()
        search = serializer.get_search()

        expected = {
            'query': {'match': {'doc_field': 'value'}},
            'sort': [{'date_created': {'order': 'desc'}}]
        }

        self.assertEqual(expected, search.to_dict())


class TestDslSortFields(TestCase):
    def test_char_sort_field_asc(self):
        search = CharSortField().get_search('doc_field')
        expected = {'sort': ['doc_field']}
        self.assertEqual(expected, search.to_dict())

    def test_char_sort_field_desc(self):
        search = CharSortField().get_search('-doc_field')
        expected = {'sort': [{'doc_field': {'order': 'desc'}}]}
        self.assertEqual(expected, search.to_dict())

    def test_choice_sort_field_asc(self):
        search = ChoiceSortField(choices=[]).get_search('doc_field')
        expected = {'sort': ['doc_field']}
        self.assertEqual(expected, search.to_dict())

    def test_choice_sort_field_desc(self):
        search = ChoiceSortField(choices=[]).get_search('-doc_field')
        expected = {'sort': [{'doc_field': {'order': 'desc'}}]}
        self.assertEqual(expected, search.to_dict())

    def test_multiple_choice_sort_field_asc(self):
        search = MultipleChoiceSortField(choices=[]).get_search(['doc_field_1', 'doc_field_2'])
        expected = {'sort': ['doc_field_1', 'doc_field_2']}
        self.assertEqual(expected, search.to_dict())

    def test_multiple_choice_sort_field_desc(self):
        search = MultipleChoiceSortField(choices=[]).get_search(['-doc_field_1', '-doc_field_2'])
        expected = {'sort': [{'doc_field_1': {'order': 'desc'}}, {'doc_field_2': {'order': 'desc'}}]}
        self.assertEqual(expected, search.to_dict())

    def test_char_list_sort_field_asc(self):
        search = CharListSortField().get_search(['doc_field_1', 'doc_field_2'])
        expected = {'sort': ['doc_field_1', 'doc_field_2']}
        self.assertEqual(expected, search.to_dict())

    def test_char_list_sort_field_desc(self):
        search = CharListSortField().get_search(['-doc_field_1', '-doc_field_2'])
        expected = {'sort': [{'doc_field_1': {'order': 'desc'}}, {'doc_field_2': {'order': 'desc'}}]}
        self.assertEqual(expected, search.to_dict())


class TestDslQueryFields(TestCase):
    def test_boolean_query_field(self):
        value = True
        search = BooleanQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_null_boolean_query_field(self):
        value = None
        search = NullBooleanQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_char_query_field(self):
        value = 'string'
        search = CharQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_email_query_field(self):
        value = 'drf_serializers@drf_util.ebs'
        search = EmailQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_regex_query_field(self):
        value = 'string'
        search = RegexQueryField(doc_field='doc_field', regex='*.').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_slug_query_field(self):
        value = 'slug'
        search = SlugQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_url_query_field(self):
        value = 'http://drf_util.ebs/drf_serializer'
        search = URLQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_uuid_query_field(self):
        value = 'sdf87f5ad8f76fd87'
        search = UUIDQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_ip_address_query_field(self):
        value = '127.0.0.1'
        search = IPAddressQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_integer_query_field(self):
        value = 111
        search = IntegerQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_float_query_field(self):
        value = 1.1
        search = FloatQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_decimal_query_field(self):
        value = 1000.0001
        search = DecimalQueryField(doc_field='doc_field', decimal_places=4, max_digits=8).get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_date_time_query_field(self):
        value = datetime.now()
        search = DateTimeQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_date_query_field(self):
        value = date.today()
        search = DateQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_time_query_field(self):
        value = time(10, 10, 10, 1000)
        search = TimeQueryField(doc_field='doc_field').get_search(value)
        expected = {'term': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_char_list_query_field(self):
        value = ['a', 'b', 'c']
        search = CharListQueryField(doc_field='doc_field').get_search(value)
        expected = {'terms': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_integer_list_query_field(self):
        value = [1, 2, 3]
        search = IntegerListQueryField(doc_field='doc_field').get_search(value)
        expected = {'terms': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())

    def test_float_list_query_field(self):
        value = [1.1, 2.2, 3.3]
        search = FloatListQueryField(doc_field='doc_field').get_search(value)
        expected = {'terms': {'doc_field': value}}
        self.assertEqual(expected, search.to_dict())


class TestDslSourceFields(TestCase):
    def test_char_source_field(self):
        search = CharSourceField().get_search('doc_field')
        expected = {'_source': ['doc_field']}
        self.assertEqual(expected, search.to_dict())

    def test_choice_source_field(self):
        search = ChoiceSourceField(choices=[]).get_search('doc_field')
        expected = {'_source': ['doc_field']}
        self.assertEqual(expected, search.to_dict())

    def test_multiple_choice_source_field(self):
        search = MultipleChoiceSourceField(choices=[]).get_search(['doc_field_1', 'doc_field_2'])
        expected = {'_source': ['doc_field_1', 'doc_field_2']}
        self.assertEqual(expected, search.to_dict())

    def test_char_list_source_field(self):
        search = CharListSourceField().get_search(['doc_field_1', 'doc_field_2'])
        expected = {'_source': ['doc_field_1', 'doc_field_2']}
        self.assertEqual(expected, search.to_dict())
