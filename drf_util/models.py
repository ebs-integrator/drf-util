from django.conf import settings
from django.db import models
from django.db.models import Manager
from django.utils import timezone
import logging
from drf_util.managers import NoDeleteManager


# ======================================================================================================================
# Common models
# ======================================================================================================================
def get_default_languages():
    return getattr(settings, 'DICT_LANG', {'en': None})


def get_lang_value(dict_data, lang=None):
    if lang is None:
        lang = getattr(settings, 'DEFAULT_LANG', 'en')

    return dict_data.get(lang, None)


class LikeLookup(models.Lookup):
    lookup_name = 'like'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f'{lhs} LIKE {rhs}', params


models.CharField.register_lookup(LikeLookup)
models.TextField.register_lookup(LikeLookup)


# ======================================================================================================================
# Abstract models
# ======================================================================================================================
class UpdateModel(models.Model):
    def update_object(self, save=True, **kwargs):
        """
        Update object by dict data, ignore data if field not exist
        :param kwargs: dict of objects, like : {field: value}
        :param save: boolean flag, if need to save object(make transaction to database)
        :return:
        """
        # if object changed, need save data
        changed = False
        for key, value in kwargs.items():
            if hasattr(self, key) and getattr(self, key) != value:
                changed = True
                setattr(self, key, value)
        # check is exist flag save and object changed
        if save and changed:
            self.save()
        return self

    class Meta:
        abstract = True


class CommonModel(UpdateModel):
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.date_updated = timezone.now()
        super(CommonModel, self).save(force_insert=force_insert, force_update=force_update, using=using,
                                      update_fields=update_fields)

    class Meta:
        ordering = ['date_created']
        abstract = True


class NoDeleteModel(models.Model):
    date_deleted = models.DateTimeField(null=True)

    objects = NoDeleteManager()
    all_objects = Manager()

    def is_deleted(self):
        return True if self.date_deleted else False

    def delete(self, *args, **kwargs):
        """
        No delete object, only change date_delete
        :param args:
        :param kwargs: hard_delete:Boolean, Use this key for real remove object from database
        :return:
        """
        if kwargs.pop("hard_delete", None):
            # hard_delete it's boolean value, for real remove object
            super(NoDeleteModel, self).delete(*args, **kwargs)
        else:
            # only change date deleted
            self.date_deleted = timezone.now()
            self.save()

    class Meta:
        abstract = True


class BaseModel(UpdateModel):
    """
        New version of CommonModel
    """
    modified_at = models.DateTimeField(auto_now=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        abstract = True


# this model works only with psycopg2
try:
    from django.contrib.postgres.fields import JSONField


    class AbstractJsonModel(models.Model):
        languages = JSONField(default=get_default_languages)

        def update_lang(self, lang, value, save=True):
            self.languages[lang] = value
            if save:
                self.save()
            return self

        def get_lang(self, lang=None):
            return get_lang_value(self.languages, lang)

        def translate(self, lang):
            return self.languages[lang]

        class Meta:
            abstract = True
except ModuleNotFoundError:
    logging.warning("psycofg2 is required for AbstractJsonModel.")
