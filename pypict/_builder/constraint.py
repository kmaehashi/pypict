import enum
import json
from typing import Dict, Iterable, Optional, Union

from pypict._builder import parameter
from pypict._builder.types import NumericType, StringType, DataTypes


"""
Implements the constraints grammar as defined in:
https://github.com/microsoft/pict/blob/main/doc/pict.md
"""


class _Operator(enum.Enum):
    _GT = '>'
    _GE = '>='
    _LT = '<'
    _LE = '<='
    _EQ = '='
    _NE = '<>'
    _IN = 'IN'
    _LIKE = 'LIKE'


class _Constraint:
    def to_string(self) -> str:
        raise NotImplemented

    def evaluate(self, combination: Dict[str, DataTypes]) -> bool:
        raise NotImplemented

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f'<PICT constraint ("{str(self)}")>'

    def __bool__(self) -> bool:
        raise ValueError('cannot apply Python logical operators on constraints')


class _Predicate(_Constraint):
    pass


class _Relation(_Predicate):
    def __init__(self,
            param: 'parameter.Parameter',
            op: _Operator,
            operand: Union[DataTypes, 'parameter.Parameter', '_ValueSet']):
        self._param = param
        self._op = op
        self._operand = operand

    def to_string(self) -> str:
        return f'{_as_str(self._param)} {self._op.value} {_as_str(self._operand)}'

    def evaluate(self, combination: Dict[str, DataTypes]) -> bool:
        if self._param.name not in combination:
            return True
        value = combination[self._param.name]
        # TODO
        if self._op is _Operator._GT:
            return value > self._operand


class _ValueSet:
    def __init__(self, values: Iterable[DataTypes]):
        self._values = values

    def to_string(self) -> str:
        return '{ ' + ', '.join([_as_str(x) for x in self._values]) + ' }'


def _as_str(v: Union[DataTypes, 'parameter.Parameter', '_ValueSet']) -> str:
    if isinstance(v, parameter.Parameter):
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
    if len(preds) == 0:
        raise ValueError('at least one predicate must be specified')
    for pred in preds:
        if not isinstance(pred, _Predicate):
            raise ValueError(f'expected predicate but got {pred} of {type(pred)}')


class _LogicalOp(_Predicate):
    _op: str = ''  # to be overridden

    def __init__(self, *preds: _Predicate):
        _check_predicates(*preds)
        self._preds = preds

    def to_string(self) -> str:
        return '(' + f' {self._op} '.join([str(x) for x in self._preds]) + ')'


class ALL(_LogicalOp):
    _op = 'AND'

    def evaluate(self, combination) -> bool:
        return all((p.evaluate(combination) for p in self._preds))


class ANY(_LogicalOp):
    _op = 'OR'

    def evaluate(self, combination) -> bool:
        return any((p.evaluate(combination) for p in self._preds))


class NOT(_Predicate):
    def __init__(self, pred: _Predicate):
        _check_predicates(pred)
        self._pred = pred

    def to_string(self) -> str:
        return f'NOT {self._pred}'

    def evaluate(self, combination: Dict[str, DataTypes]) -> bool:
        return not self._pred.evaluate(combination)


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

    def evaluate(self, combination) -> bool:
        if self._then is None:
            raise ValueError('cannot evaluate without THEN')
        if self._if.evaluate(combination):
            return self._then.evaluate(combination)
        elif self._else is not None:
            return self._else.evaluate(combination)
        return True
