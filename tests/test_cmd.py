import unittest

from pypict import cmd


_model = '''
X: 1, 2
Y: 3, 4
'''
_header = ['X', 'Y']
_rows = [['2', '4'], ['2', '3'], ['1', '4'], ['1', '3']]


class TestCmd(unittest.TestCase):
    def test_usecase_simple(self):
        for sub in [False, True]:
            actual_header, actual_rows = cmd.from_model(
                    _model, use_subprocess=sub)
            assert actual_header == _header
            assert actual_rows == _rows
