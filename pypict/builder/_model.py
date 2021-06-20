from typing import Iterable, Iterator, List, Optional, Tuple, Type, Union

from pypict.builder._parameter import Parameter
from pypict.builder._constraint import _Constraint


class Model:
    def __init__(self):
        self._parameters: List[Parameter] = []
        self._submodels: List[_SubModel] = []
        self._constraints: List[_Constraint] = []

    def parameters(self, *params: Parameter) -> 'Model':
        # TODO check uniqueness of names
        self._parameters += params
        return self
    
    def submodel(self, params: Tuple[Parameter], order: Optional[int] = None) -> 'Model':
        self._submodels.append(_SubModel(params, order))
        return self

    def constraints(self, *constraints: _Constraint) -> 'Model':
        self._constraints += constraints
        return self

    def to_string(self) -> str:
        lines: List[str] = []

        # Parameter definitions
        if len(self._parameters) == 0:
            raise ValueError('no parameters are added to the model')
        for p in self._parameters:
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
                lines.append('')

        return '\n'.join(lines)


class _SubModel:
    def __init__(self, params: Tuple[Parameter], order: Optional[int] = None):
        self.params = params
        self.order = order

    def to_string(self) -> str:
        return (
            '{ ' +
                ', '.join([param.name for param in self.params]) +
            ' }' +
            '' if self.order is None else f' @ {self.order}'
        )
