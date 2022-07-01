from django.utils import timezone
from django.db import models


class QuerySet(models.query.QuerySet):
    def _fetch_all(self):
        if self._result_cache is None:
            query = self

            fetch_only_annotation = self.query.__dict__.get('fetch_only_annotation')
            if fetch_only_annotation:
                query = query.annotate(**fetch_only_annotation)

            self._result_cache = list(self._iterable_class(query))
        if self._prefetch_related_lookups and not self._prefetch_done:
            self._prefetch_related_objects()

    def fetch_only_annotation(self, **kwargs):
        if 'fetch_only_annotation' not in self.query.__dict__:
            self.query.__dict__['fetch_only_annotation'] = kwargs
        else:
            self.query.__dict__['fetch_only_annotation'].update(kwargs)

        return self


class BaseManager(models.manager.BaseManager.from_queryset(QuerySet)):
    pass


class NoDeleteQuerySet(QuerySet):
    def delete(self):
        self.update(date_deleted=timezone.now())
        return self.count(), None


class NoDeleteManager(BaseManager.from_queryset(NoDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(date_deleted__isnull=True)
