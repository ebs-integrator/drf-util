from django.db import models


class NoDeleteManager(models.Manager):
    def get_queryset(self):
        return super(NoDeleteManager, self).get_queryset().filter(date_deleted__isnull=True)
