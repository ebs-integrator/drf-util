from django.db.models import Model, CharField
from drf_util.models import NoDeleteModel


class Thing(NoDeleteModel, Model):
    title = CharField(max_length=63)

    class Meta:
        db_table = 'things'
