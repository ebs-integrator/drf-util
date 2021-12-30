from django.utils.translation import gettext_lazy as _
from rest_framework import relations


class ManyRelatedField(relations.ManyRelatedField):
    default_error_messages = {
        **relations.ManyRelatedField.default_error_messages,
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid pks "{pk_value}" - objects do not exist.'),
        'incorrect_type': _('Incorrect type. Expected pk value, received {data_type}.'),
    }

    def to_internal_value(self, data):
        if isinstance(data, str) or not hasattr(data, '__iter__'):
            self.fail('not_a_list', input_type=type(data).__name__)
        if not self.allow_empty and len(data) == 0:
            self.fail('empty')

        items = list(self.child_relation.get_queryset().filter(pk__in=data))
        if len(items) != len(data):
            items_ids = [item.id for item in items]
            not_valid_items = [str(item) for item in data if item not in items_ids]
            raise self.fail('does_not_exist', pk_value=', '.join(not_valid_items))

        return items


class PrimaryKeyRelatedField(relations.PrimaryKeyRelatedField):
    @property
    def request(self):
        return self.context.get('request')

    def get_queryset(self):
        queryset = super().get_queryset()
        protected_lookup_function = getattr(self.queryset.model(), 'get_protected_lookup_query', None)
        if protected_lookup_function:
            query = protected_lookup_function(self.request.account)
            queryset = queryset.filter(query)
        return queryset

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in relations.MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedField(**list_kwargs)
