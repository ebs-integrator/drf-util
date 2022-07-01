from django.db import models


class Not(models.Transform):  # noqa
    function = 'NOT'
    lookup_name = 'not'


class Distinct(models.Lookup):
    lookup_name = 'distinct'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f'{lhs} IS DISTINCT FROM {rhs}', params


class LikeLookup(models.Lookup):
    lookup_name = 'like'

    def as_sql(self, compiler, connection):
        lhs, lhs_params = self.process_lhs(compiler, connection)
        rhs, rhs_params = self.process_rhs(compiler, connection)
        params = lhs_params + rhs_params
        return f'{lhs} LIKE {rhs}', params


models.Field.register_lookup(Not)
models.Field.register_lookup(Distinct)
models.CharField.register_lookup(LikeLookup)
models.TextField.register_lookup(LikeLookup)
