# ----------------------------------------------------------------------------
# Copyright (c) 2016-2019, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

import json


from qiime2.core.type.template import TypeTemplate, instantiate

def is_collection_type(x):
    raise TypeError

class _CollectionBase(TypeTemplate):
    def __init__(self, fields=()):
        self.fields = fields

    def __eq__(self, other):
        return type(self) is type(other) and self.fields == other.fields

    def get_name(self):
        return self.__class__.__name__

    def get_kind_expr(self, self_expr):
        if self_expr.fields:
            return self_expr.fields[0].kind
        return ""

    def get_kind(self):
        raise NotImplementedError

    def is_variant(self):
        return False

    def validate_predicate(self, predicate, expr):
        raise TypeError("Predicates cannot be applied to %r" % expr)

    def validate_field(self, name, field):
        if isinstance(field, self.__class__):
            raise TypeError

    def validate_union(self, other):
        if type(other) is not type(self):
            raise TypeError

    def is_element_expr(self, self_expr, value):
        contained_expr = self_expr.fields[0]
        if isinstance(value, self._view) and len(value) > 0:
            return all(v in contained_expr for v in value)
        return False

    def is_element(self, value):
        raise NotImplementedError

    def validate_intersection(self, other):
        pass

    def to_ast(self):
        ast = super().to_ast()
        ast['type'] = "collection"
        return ast


class _1DCollectionBase(_CollectionBase):
    def get_field_names(self):
        return ['type']


@instantiate
class Set(_1DCollectionBase):
    _view = set

@instantiate
class List(_1DCollectionBase):
    _view = list

@instantiate
class Tuple(_CollectionBase):
    _view = tuple

    def get_kind_expr(self, self_expr):
        return ""

    def get_field_names(self):
        return ['*types']

    def validate_field_count(self, count):
        if not count:
            raise TypeError("Tuple type must contain at least one element.")

    def validate_field(self, name, field):
        # Tuples may contain anything, and as many fields as desired
        pass


