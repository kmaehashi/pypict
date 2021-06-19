
import pypict.builder


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


class _Relation(_Constraint):
    def __init__(self, param, op, value_or_param):
        self._param = param
        self._op = op
        self._value_or_param = value_or_param

    def to_string(self) -> str:
        return f'{_literal(self._param)} {self._op} {_literal(self._value_or_param)}'


class _LogicalOp(_Constraint):
    _op: str = None  # to be overridden

    def __init__(self, *consts: _Constraint):
        for const in consts:
            if not isinstance(const, _Constraint):
                raise ValueError
        self._consts = consts

    def to_string(self) -> str:
        return '(' + f' {self._op} '.join([str(x) for x in self._consts]) + ')'


class AND(_LogicalOp):
    _op = 'AND'


class OR(_LogicalOp):
    _op = 'OR'


class NOT(_Constraint):
    def __init__(self, const: _Constraint):
        if not isinstance(const, _Constraint):
            raise ValueError
        self._const = const

    def to_string(self) -> str:
        return f'NOT {self._const}'


class IF(_Constraint):
    def __init__(self, const: _Constraint):
        if not isinstance(const, _Constraint):
            raise ValueError
        self._const = const
        self._then = None
        self._else = None
    
    def THEN(self, const: _Constraint) -> 'IF':
        if self._then is not None:
            raise ValueError
        self._then = const
        return self
    
    def ELSE(self, const: _Constraint) -> 'IF':
        if self._then is None:
            raise ValueError
        if self._else is None:
            raise ValueError
        self._else = const

    def to_string(self) -> str:
        if self._then is None:
            raise ValueError
        return (
            f'IF {self._const}' +
            f'\nTHEN {self._then}' +
            (f'\nELSE {self._else}' if self._else else '')
        )


class _ValueSet:
    def __init__(self, values):
        self._values = values

    def to_string(self) -> str:
        return '{ ' + ', '.join([_literal(x) for x in self._values]) + ' }'


def _literal(v):
    if isinstance(v, pypict.builder.Parameter):
        return f'[{v._name}]'
    elif isinstance(v, _ValueSet):
        return v.to_string()
    elif isinstance(v, str):
        return f'"{v}"'  # TODO check?
    else:
        return str(v)