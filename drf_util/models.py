from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Manager
from django.utils import timezone

from drf_util.managers import NoDeleteManager

# getting user model (Custom or Default)
User = get_user_model()


# ======================================================================================================================
# Common models
# ======================================================================================================================
def get_default_languages():
    return getattr(settings, 'DICT_LANG', {'en': None})


def get_lang_value(dict_data, lang=None):
    if lang is None:
        lang = getattr(settings, 'DEFAULT_LANG', 'en')

    return dict_data.get(lang, None)


# ======================================================================================================================
# Abstract models
# ======================================================================================================================
class CommonModel(models.Model):
    date_created = models.DateTimeField(default=timezone.now)
    date_updated = models.DateTimeField(default=timezone.now)

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
