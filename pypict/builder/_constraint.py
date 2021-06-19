
from pypict.builder._export import _literal


class _Constraint:
    def to_string(self):
        raise NotImplemented

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f'<PICT Constraint ("{str(self)}")>'


class _Relation(_Constraint):
    def __init__(self, param, op, value_or_param):
        self._param = param
        self._op = op
        self._value_or_param = value_or_param

    def to_string(self):
        return f'{_literal(self._param)} {self._op} {_literal(self._value_or_param)}'


class _LogicalOp(_Constraint):
    _op = None

    def __init__(self, consts):
        self._consts = consts

    def to_string(self):
        return '(' + f' {self._op} '.join([str(x) for x in self._consts]) + ')'


class AND(_LogicalOp):
    _op = 'AND'


class OR(_LogicalOp):
    _op = 'OR'


class NOT(_Constraint):
    def __init__(self, const):
        self._const = const

    def to_string(self):
        return f'NOT {self._const}'


class IF(_Constraint):
    def __init__(self, const):
        self._const = const
        self._then = None
        self._else = None
    
    def THEN(self, const):
        if self._then is not None:
            raise ValueError
        self._then = const
        return self
    
    def ELSE(self, const):
        if self._then is None:
            raise ValueError
        if self._else is None:
            raise ValueError
        self._else = const

    def to_string(self):
        if self._then is None:
            raise ValueError
        return (
            f'IF {self._const}' +
            f'\nTHEN {self._then}' +
            (f'\nELSE {self._else}' if self._else else '') +
            ';'
        )
