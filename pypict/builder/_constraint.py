import json
from typing import Iterable, Optional, Union

from pypict.builder import _parameter
from pypict.builder._types import NumericType, StringType, DataTypes


"""
Implements the constraints grammar as defined in:
https://github.com/microsoft/pict/blob/main/doc/pict.md
"""


class _Constraint:
    def to_string(self) -> str:
        raise NotImplemented

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f'<PICT constraint ("{str(self)}")>'


class _Predicate(_Constraint):
    pass


class _Relation(_Predicate):
    def __init__(self,
            param: '_parameter.Parameter',
            op: str,
            operand: Union[DataTypes, '_parameter.Parameter', '_ValueSet']):
        self._param = param
        self._op = op
        self._operand = operand

    def to_string(self) -> str:
        return f'{_as_str(self._param)} {self._op} {_as_str(self._operand)}'


class _ValueSet:
    def __init__(self, values: Iterable[DataTypes]):
        self._values = values

    def to_string(self) -> str:
        return '{ ' + ', '.join([_as_str(x) for x in self._values]) + ' }'


def _as_str(v: Union[DataTypes, '_parameter.Parameter', '_ValueSet']) -> str:
    if isinstance(v, _parameter.Parameter):
        return f'[{v.name}]'
    elif isinstance(v, _ValueSet):
        return v.to_string()
    elif isinstance(v, NumericType):
        return str(v)
    elif isinstance(v, StringType):
        # Escape double-quotes in the string then quote the entire string.
        return json.dumps(v)
    raise ValueError(v)


def _check_predicates(*preds: _Predicate):
    for pred in preds:
        if not isinstance(pred, _Predicate):
            raise ValueError(f'expected predicate but got {pred} of {type(pred)}')


class _LogicalOp(_Predicate):
    _op: Optional[str] = None  # to be overridden

    def __init__(self, *preds: _Predicate):
        _check_predicates(*preds)
        self._preds = preds

    def to_string(self) -> str:
        return '(' + f' {self._op} '.join([str(x) for x in self._preds]) + ')'


class ALL(_LogicalOp):
    _op = 'AND'


class ANY(_LogicalOp):
    _op = 'OR'


class NOT(_Predicate):
    def __init__(self, pred: _Predicate):
        _check_predicates(pred)
        self._pred = pred

    def to_string(self) -> str:
        return f'NOT {self._pred}'


class IF(_Constraint):
    def __init__(self, pred: _Predicate):
        _check_predicates(pred)
        self._if = pred
        self._then: Optional[_Predicate] = None
        self._else: Optional[_Predicate] = None

    def THEN(self, pred: _Predicate) -> 'IF':
        _check_predicates(pred)
        if self._then is not None:
            raise ValueError('THEN cannot be repeated')
        self._then = pred
        return self

    def ELSE(self, pred: _Predicate) -> 'IF':
        _check_predicates(pred)
        if self._then is None:
            raise ValueError('THEN must be given before ELSE')
        if self._else is not None:
            raise ValueError('ELSE cannot be repeated')
        self._else = pred

    def to_string(self) -> str:
        if self._then is None:
            raise ValueError('THEN must be given')
        return (
            f'IF {self._if}' +
            f'\nTHEN {self._then}' +
            (f'\nELSE {self._else}' if self._else else '')
        )
