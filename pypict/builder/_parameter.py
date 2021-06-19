import numbers
from typing import Iterable, Iterator, List, Optional, Tuple, Type, Union

from pypict.builder._constraint import _Relation
from pypict.builder._export import _literal, _ValueSet


NumericType = numbers.Real
StringType = str
DataTypes = Union[NumericType, StringType]


class Parameter:
    def __init__(
            self,
            name: str,
            values: Iterable[Union[DataTypes, Tuple[DataTypes, int]]],
            *,
            aliases: Optional[Iterable[str]] = None):
        if aliases is None:
            aliases = []
        numeric = self._check_values(values)

        self._check_valid_name(name)
        for x in aliases:
            self._check_valid_name(x)

        self._name = name
        self._values = values
        self._aliases = aliases
        self._numeric = numeric

    @staticmethod
    def _check_valid_name(name):
        if '[' in name or ']' in name:
            raise ValueError(f'invalid parameter name: {name}')

    @staticmethod
    def _check_values(
            values: Iterable[Union[DataTypes, Tuple[DataTypes, int]]]) -> bool:
        numeric = True
        for i, x in enumerate(values):
            if isinstance(x, tuple):
                value, weight = x
            else:
                value, weight = x, 1
            if isinstance(value, NumericType):
                pass
            elif isinstance(value, StringType):
                numeric = False
            else:
                raise ValueError(
                    f'unsupported data type at index {i}: {value} ({type(value)})')
            if not isinstance(weight, int):
                raise ValueError
        return numeric

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return self.to_string()  # TODO

    def to_string(self, separator=','):
        values = f'{separator} '.join([str(x) for x in self._values])
        return f'{self._name}: {values}'

    def _check_operand(self, other, *, allow_string=False):
        if isinstance(other, Parameter):
            if self._numeric != other._numeric:
                raise ValueError
        elif isinstance(other, NumericType):
            if not self._numeric:
                raise ValueError
        elif isinstance(other, StringType):
            if not allow_string:
                raise ValueError
            if self._numeric:
                raise ValueError
        else:
            raise ValueError

    def __eq__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other, allow_string=True)
        return _Relation(self, '=', other)

    def __ne__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other, allow_string=True)
        return _Relation(self, '<>', other)

    def __gt__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other)
        return _Relation(self, '>', other)

    def __ge__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other)
        return _Relation(self, '>=', other)

    def __lt__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other)
        return _Relation(self, '<', other)

    def __le__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other)
        return _Relation(self, '<=', other)

    def __in__(self, values: Iterable[DataTypes]):
        return _Relation(self, 'IN', _ValueSet(values))

    def like(self, value):
        if self._dtype != str:
            raise ValueError
        return _Relation(self, 'LIKE', value)
