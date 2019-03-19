import itertools
from types import MappingProxyType

from ..util import superscript, tuplize
from .grammar import UnionExp, TypeExp
from .collection import Tuple, List, Set
from .poset import POSet


class TypeVarExp(UnionExp):
    def __init__(self, members, tmap, input=False, output=False, index=None):
        super().__init__(members)
        self.mapping = tmap
        self.input = input
        self.output = output
        self.index = index

    def __repr__(self):
        numbers = {}
        for idx, m in enumerate(self.members):
            if m in numbers:
                numbers[m] += superscript(',' + str(idx))
            else:
                numbers[m] = superscript(idx)
        return " or ".join([repr(k) + v for k, v in numbers.items()])

    def is_defined(self):
        return False

    def uniq_upto_sub(self, a_expr, b_expr):
        """
        Two elements are unique up to a subtype if they are indistinguishable
        with respect to that subtype. In the case of a type var, that means
        the same branches must be "available" in the type map.

        This means that A or B may have additional refinements (or may even be
        subtypes of each other), so long as that does not change the branch
        chosen by the type map.

        """
        a_branches = [m for m in self.members if a.expr <= m]
        b_branches = [m for m in self.members if b.expr <= m]
        return a_branches == b_branches

    def __eq__(self, other):
        return self.index == other.index and self.mapping == other.mapping

    def __hash__(self):
        return hash(self.index) ^ hash(self.mapping)


class TypeMap:
    def __init__(self, mapping):
        unsorted = {Tuple[tuplize(k)]: Tuple[tuplize(v)]
                    for k, v in mapping.items()}

        poset = POSet(*unsorted)
        for a, b in itertools.combinations(poset.iter_nodes(), 2):
            intersection = a.item & b.item
            if (intersection.is_bottom()
                    or intersection is a.item
                    or intersection is b.item):
                continue

            for shared in a.shared_decendents(b):
                if intersection <= shared.item:
                    break
            else:
                raise ValueError("Ambiguous resolution for invocations with"
                                 " type %r. Could match %r or %r, add a new"
                                 " branch (or modify these branches) to"
                                 " correct this." % (intersection.fields,
                                                     a.item.fields,
                                                     b.item.fields))

        self.lifted = MappingProxyType({k: unsorted[k] for k in poset})

    def __eq__(self, other):
        return self is other

    def __hash__(self):
        return hash(id(self))

    def __iter__(self):
        for idx, members in enumerate(
                zip(*(k.fields for k in self.lifted.keys()))):
            yield TypeVarExp(members, self, input=True, index=idx)

        yield from self.iter_outputs()

    def solve(self, *inputs):
        inputs = Tuple[inputs]
        for branch, outputs in self.lifted.items():
            if inputs <= branch:
                return outputs.fields

    def input_width(self):
        return len(next(iter(self.lifted.keys())).fields)

    def iter_outputs(self):
        start = self.input_width()
        for idx, members in enumerate(
                zip(*(v.fields for v in self.lifted.values())), start):
            yield TypeVarExp(members, self, output=True, index=idx)


def _get_intersections(listing):
    intersections = []
    for a, b in itertools.combinations(listing, 2):
        i = a & b
        if i.is_bottom() or i is a or i is b:
            continue
        intersections.append(i)
    return intersections


def TypeMatch(listing):
    listing = list(listing)
#    intersections = _get_intersections(listing)
#    while intersections:
#        listing.extend(intersections)
#        intersections = _get_intersections(intersections)
    mapping = TypeMap({l: l for l in listing})
    for var in mapping.iter_outputs():  # used by match
        var.input = True
        return var  # typematch only matches one variable


def has_variables(expr):
    return bool(list(select_variables(expr)))


def select_variables(expr):
    """When called on an expression, will yield selectors to the variable.

    A selector will either return the variable (or equivalent fragment) in
    an expression, or will return an entirely new expression with the
    fragment replaced with the value of `swap`.

    e.g.
    >>> select_u, select_t = select_variables(Example[T] % U)
    >>> t = select_t(Example[T] % U)
    >>> assert T is t
    >>> u = select_u(Example[T] % U)
    >>> assert U is u

    >>> frag = select_t(Example[Foo] % Bar)
    >>> assert frag is Foo
    >>> new_expr = select_t(Example[T] % U, swap=frag)
    >>> assert new_expr == Example[Foo] % U

    """
    if type(expr) is TypeVarExp:
        def select(x, swap=None):
            if swap is not None:
                return swap
            return x

        yield select
        return

    if type(expr) is not TypeExp:
        return

    if type(expr.full_predicate) is TypeVarExp:
        def select(x, swap=None):
            if swap is not None:
                return x.duplicate(predicate=swap)
            return x.full_predicate

        yield select

    for idx, field in enumerate(expr.fields):
        for sel in select_variables(field):
            def select(x, swap=None):
                if swap is not None:
                    new_fields = list(x.fields)
                    new_fields[idx] = sel(x.fields[idx], swap)
                    return x.duplicate(fields=tuple(new_fields))
                return x.fields[idx]

            yield select


def match(provided, inputs, outputs):
    provided_binding = {}
    error_map = {}
    for key, expr in inputs.items():
        for selector in select_variables(expr):
            var = selector(expr)
            provided_fragment = selector(provided[key])
            try:
                current_binding = provided_binding[var]
            except KeyError:
                provided_binding[var] = provided_fragment
                error_map[var] = expr
            else:
                if not var.uniq_upto_sub(current_binding, provided_fragment):
                    raise ValueError("Received %r and %r, but expected %r"
                                     " and %r to match (or to select the same"
                                     " output)."
                                     % (error_map[var], expr, current_binding,
                                        provided_fragment))
    del error_map

    # provided_binding now maps TypeVarExp instances to a TypeExp instance
    # which is the relevent fragment from the provided input types

    grouped_maps = {}
    for item in provided_binding.items():
        var = item[0]
        if var.mapping not in grouped_maps:
            grouped_maps[var.mapping] = [item]
        else:
            grouped_maps[var.mapping].append(item)

    # grouped_maps now maps a TypeMap instance to tuples of
    # (TypeVarExp, TypeExp) which are the items of provided_binding
    # i.e. all of the bindings are now grouped under their shared type maps

    output_fragments = {}
    for mapping, group in grouped_maps.items():
        if len(group) != mapping.input_width():
            raise ValueError("Missing input variables")

        inputs = [x[1] for x in sorted(group, key=lambda x: x[0].index)]
        solved = mapping.solve(*inputs)
        if solved is None:
            raise ValueError("No solution.")

        # type vars share identity by instance of map and index, so we will
        # be able to see the "same" vars again when looking up the outputs
        for var, out in zip(mapping.iter_outputs(), solved):
            output_fragments[var] = out

    # output_fragments now maps a TypeVarExp to a TypeExp which is the solved
    # fragment for the given output type variable

    results = {}
    for key, expr in outputs.items():
        r = expr  # output may not have a typevar, so default is the expr
        for selector in select_variables(expr):
            var = selector(expr)
            r = selector(r, swap=output_fragments[var])
        results[key] = r

    # results now maps a key to a full TypeExp as solved by the inputs
    return results