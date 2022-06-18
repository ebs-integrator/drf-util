from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

DEFAULT_PAGE = 1


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

    @property
    def count(self):
        paginator = getattr(self.page, 'paginator', None)
        return paginator.count if paginator else None

    @property
    def num_pages(self):
        paginator = getattr(self.page, 'paginator', None)
        return paginator.num_pages if paginator else None

    def paginate_queryset(self, *args, **kwargs):
        try:
            return super().paginate_queryset(*args, **kwargs)
        except NotFound as e:
            return list()
