from django.db import models
from drf_util.models import NoDeleteModel, BaseModel


class Thing(NoDeleteModel, models.Model):
    title = models.CharField(max_length=63)
    another_thing = models.ForeignKey('AnotherThing', on_delete=models.CASCADE, related_name='things', null=True)
    other_things = models.ManyToManyField('OtherThing', blank=True)

    class Meta:
        db_table = 'things'


class OtherThing(BaseModel):
    title = models.CharField(max_length=20)
    another_thing = models.ForeignKey('AnotherThing', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'other_things'


class AnotherThing(BaseModel):
    title = models.CharField(max_length=20)

    class Meta:
        db_table = 'another_things'
