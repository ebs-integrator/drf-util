from django.utils.translation import gettext as _
from elasticsearch import Elasticsearch, helpers
from rest_framework.exceptions import ValidationError


class ElasticUtil(object):
    hosts = []
    index_prefix = ''

    max_result_window = 10000
    known_indexes = []

    def __init__(self, **kwargs):
        self.session = Elasticsearch(hosts=self.hosts, timeout=50, **kwargs)
        self.build_index_names()

    def build_index_names(self, prefix=None):
        self.known_indexes = []
        for key, value in self.__class__.__dict__.items():
            if key.endswith('_index') and isinstance(key, str):
                if prefix and not prefix in value:
                    index_name = self.index_prefix + '_' + prefix + value
                else:
                    index_name = self.index_prefix + '_' + value

                setattr(self, key, index_name)
                self.known_indexes.append(index_name)

    def search(self, index, body, doc_type=None):
        response = self.session.search(index=index, doc_type=doc_type if doc_type else index, body=body)
        return response['hits']['hits'], response['hits']['total']

    def count(self, index, body, doc_type=None):
        response = self.session.count(index=index, doc_type=doc_type if doc_type else index, body=body)
        return response['count']

    def add_document(self, index, document, doc_type=None, document_id=None):
        result = self.session.index(
            index=index,
            doc_type=doc_type if doc_type else index,
            body=document,
            id=document_id
        )
        return result["result"]

    def insert_bulk(self, body):
        return helpers.bulk(self.session, body)

    def init_indexes(self):
        # create indexes
        for index in self.known_indexes:
            self.session.indices.create(index=index, ignore=400)

    def use_for_testing(self):
        # change indexes
        self.build_index_names('test_')
        self.init_indexes()

    def delete_test_indexes(self):
        self.session.indices.delete(index=self.index_prefix + "_test_*")

    def get_source(self, hit, context=None):
        source = hit['_source']
        if 'labels' in source:
            del source['labels']
        return source

    def search_response(self, serializer, index, prepare_function=None, context=None, query=None):
        size = serializer.get_default_per_page()
        skip = serializer.get_skip()

        if size + skip > self.max_result_window:
            raise ValidationError({
                'page': [_('Result window must be less than or equal to %s') % self.max_result_window]
            })

        results, count = self.search(index, {
            "from": skip,
            "size": size,
            "sort": serializer.sort_criteria,
            "query": {"bool": query} if query else {"bool": {"must": serializer.get_filter()}}
        })

        if prepare_function is None:
            prepare_function = self.get_source

        prepared_results = []
        for result in results:
            prepared_results.append(prepare_function(result, context))

        return {
            'data': serializer.get_fetched(prepared_results),
            'total_results': count if count < self.max_result_window else self.max_result_window,
            'total': count,
            'per_page': serializer.get_default_per_page(),
            'page': serializer.get_page(),
        }
