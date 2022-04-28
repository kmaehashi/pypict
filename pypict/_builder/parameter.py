from typing import Iterable, Tuple, Union

from pypict._builder import constraint
from pypict._builder.dtype import NumericType, StringType, DataTypes


# Values can be a list of (literals or tuple of (literal, weight)).
ValuesType = Iterable[Union[DataTypes, Tuple[DataTypes, int]]]


class Parameter:
    def __init__(self, name: str, values: ValuesType):
        # TODO support aliases
        if ':' in name:
            raise ValueError(f'invalid parameter name: {name}')
        self.name = name
        self.values = values
        self._is_numeric = self._check_values(values)

    @staticmethod
    def _check_values(values: ValuesType) -> bool:
        is_numeric = True
        for x in values:
            if isinstance(x, tuple):
                value, weight = x
            else:
                value, weight = x, 1
            if isinstance(value, NumericType):
                pass
            elif isinstance(value, StringType):
                is_numeric = False
            else:
                raise ValueError(
                    'expected numeric or string, '
                    f'but got {value} of {type(value)}')
            if not isinstance(weight, int):
                raise ValueError(
                    'weight must be int, '
                    f'but got {weight} of {type(weight)}')
        return is_numeric

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self) -> str:
        return f'<PICT parameter ({self.name})>'

    def to_string(self, separator: str = ',') -> str:
        return self.name + ': ' + f'{separator} '.join([
            f'{x[0]} ({x[1]})' if isinstance(x, tuple) else str(x)
            for x in self.values
        ])

    def _check_operand(
            self,
            other: Union[DataTypes, 'Parameter'],
            *,
            no_string: bool = False):
        if isinstance(other, Parameter):
            if self._is_numeric != other._is_numeric:
                raise ValueError(
                    'cannot compare numeric and non-numeric parameters')
        elif isinstance(other, NumericType):
            if not self._is_numeric:
                raise ValueError(
                    'cannot compare string-typed parameter '
                    'with numeric constant')
        elif isinstance(other, StringType):
            if no_string:
                raise ValueError('strings cannot be compared')
            if self._is_numeric:
                raise ValueError(
                    'cannot compare numeric-typed parameter '
                    'with string constant')
        else:
            raise ValueError(f'cannot compare with {other} of {type(other)}')

    def __gt__(self, other: Union[NumericType, 'Parameter']):
        self._check_operand(other, no_string=True)
        return constraint._Relation(self, constraint._Operator._GT, other)

    def __ge__(self, other: Union[NumericType, 'Parameter']):
        self._check_operand(other, no_string=True)
        return constraint._Relation(self, constraint._Operator._GE, other)

    def __lt__(self, other: Union[NumericType, 'Parameter']):
        self._check_operand(other, no_string=True)
        return constraint._Relation(self, constraint._Operator._LT, other)

    def __le__(self, other: Union[NumericType, 'Parameter']):
        self._check_operand(other, no_string=True)
        return constraint._Relation(self, constraint._Operator._LE, other)

    def __eq__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other)
        return constraint._Relation(self, constraint._Operator._EQ, other)

    def __ne__(self, other: Union[DataTypes, 'Parameter']):
        self._check_operand(other)
        return constraint._Relation(self, constraint._Operator._NE, other)

    def IN(self, *values: DataTypes):
        for x in values:
            self._check_operand(x)
        return constraint._Relation(
            self, constraint._Operator._IN, constraint._ValueSet(values))

    def LIKE(self, value: StringType):
        if self._is_numeric:
            raise ValueError('LIKE operator is only for string parameter')
        if not isinstance(value, StringType):
            raise ValueError(
                'expected wildcard pattern string, '
                f'but got {value} of {type(value)}')
        return constraint._Relation(self, constraint._Operator._LIKE, value)
