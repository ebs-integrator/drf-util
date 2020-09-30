from django.utils import timezone
from django.db import models
from django.db.models.manager import BaseManager


class NoDeleteQuerySet(models.query.QuerySet):
    def delete(self):
        self.update(date_deleted=timezone.now())
        return self.count(), None


class NoDeleteManager(BaseManager.from_queryset(NoDeleteQuerySet)):
    def get_queryset(self):
        return super().get_queryset().filter(date_deleted__isnull=True)
