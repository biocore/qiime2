
from abc import ABCMeta, abstractmethod
import itertools


from qiime2.core.type.grammar import (IncompleteExp, TypeExp, PredicateExp,
                                      IntersectionExp)



def instantiate(cls):
    return cls()


class _BaseTemplate(metaclass=ABCMeta):
    public_proxy = ()

    @abstractmethod
    def __eq__(self, other):
        raise NotImplementedError

    def __hash__(self, other):
        return 0

    def get_name_expr(self, self_expr):
        return self.get_name()

    @abstractmethod
    def get_name(self):
        raise NotImplementedError

    def get_kind_expr(self, self_expr):
        return self.get_kind()

    @abstractmethod
    def get_kind(self):
        raise NotImplementedError

    def validate_union_expr(self, self_expr, other_expr):
        return self.validate_union(other_expr.template)

    @abstractmethod
    def validate_union(self, other):
        raise NotImplementedError

    def validate_intersection_expr(self, self_expr, other_expr):
        return self.validate_intersection(other_expr.template)

    @abstractmethod
    def validate_intersection(self, other):
        raise NotImplementedError

    def is_element_expr(self, self_expr, value):
        return self.is_element(value)

    @abstractmethod
    def is_element(self, value):
        raise NotImplementedError

    def collapse_intersection(self, other):
        return NotImplemented

    def is_symbol_subtype_expr(self, self_expr, other_expr):
        return self.is_symbol_subtype(other_expr.template)

    def is_symbol_subtype(self, other):
        return self.get_name() == other.get_name()

    def is_symbol_supertype_expr(self, self_expr, other_expr):
        return self.is_symbol_supertype(other.template)

    def is_symbol_supertype(self, other):
        return self.get_name() == other.get_name()


class TypeTemplate(_BaseTemplate):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)

        if list(self.get_field_names()):
            return IncompleteExp(self)
        else:
            return TypeExp(self)

    def get_field_names_expr(self, expr):
        return self.get_field_names()

    @abstractmethod
    def get_field_names(self):
        raise NotImplementedError

    def validate_fields_expr(self, self_expr, fields_expr):
        self.validate_field_count(len(fields_expr))
        for expr, name in itertools.zip_longest(fields_expr,
                                                self.get_field_names(),
                                                fillvalue=IntersectionExp()):
            if expr.template is None:
                for exp in expr.members:
                    if exp.template is None:
                        for ex in exp.members:
                            self.validate_field(name, ex.template)
                    else:
                        self.validate_field(name, exp.template)
            else:
                self.validate_field(name, expr.template)

    def validate_field_count(self, count):
        if count != len(self.get_field_names()):
            raise TypeError

    @abstractmethod
    def validate_field(self, name, field):
        raise NotImplementedError

    def validate_predicate_expr(self, self_expr, predicate_expr):
        if predicate_expr.template is None:
            for predicate in predicate_expr.members:
                self.validate_predicate_expr(self_expr, predicate)
        else:
            self.validate_predicate(predicate_expr.template)

    @abstractmethod
    def validate_predicate(self, predicate):
        raise NotImplementedError


class PredicateTemplate(_BaseTemplate):
    def __new__(cls, *args, **kwargs):
        self = super().__new__(cls)
        self.__init__(*args, **kwargs)
        return PredicateExp(self)

    @abstractmethod
    def __hash__(self, other):
        raise NotImplementedError