from typing import Iterable, Iterator, List, Optional, Tuple, Type, Union

from pypict.builder._parameter import Parameter
from pypict.builder._constraint import _Constraint


class Model:
    def __init__(self):
        self._params = []
        self._submodels = []
        self._constraints = []

    def parameters(self, *params: Parameter) -> 'Model':
        self._params += params
        return self
    
    def submodel(self, params: Tuple[Parameter], order: Optional[int] = None) -> 'Model':
        self._submodels.append(_SubModel(params, order))
        return self

    def constraints(self, *constraints: _Constraint) -> 'Model':
        self._constraints += constraints
        return self

    def to_string(self):
        lines = []

        # Parameter definitions
        if len(self._params) == 0:
            raise ValueError('no parameters are added to the model')
        for p in self._params:
            lines.append(p.to_string())
        lines.append('')

        # Sub-model definitions
        if len(self._submodels) != 0:
            for s in self._submodels:
                lines.append(s.to_string())
            lines.append('')

        # Constraint definitions
        if len(self._constraints) != 0:
            for c in self._constraints:
                lines.append(c.to_string() + ';')
        
        return '\n'.join(lines)


class _SubModel:
    def __init__(self, params, order=None):
        self._params = params
        self._order = order

    def to_string(self):
        return (
            '{ ' +
                ', '.join([param._name for param in self._params]) +
            ' }' +
            '' if self._order is None else f' @ {self._order}'
        )