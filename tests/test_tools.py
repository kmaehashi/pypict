from datetime import datetime
import unittest

from pypict.cmd import from_model

from pypict.tools import from_dict
from pypict.tools import compose_filter_funcs
from pypict.tools import product
from pypict.tools import _populate_exclusion_rules


###
### Model Definition (for Command API)
###

_model = '''
# Test Axes
base:       ubuntu14, ubuntu16, centos6, centos7
python:     2.7, 3.4, 3.5, 3.6
numpy:      1.9, 1.10, 1.11, 1.12, 1.13, 1.14
scipy:      None, 0.19
ideep:      None, 1.0.4
cuda:       7, 7.5, 8.0, 9.0, 9.1
cudnn:      None, 4, 5, 5.1, 6, 7
nccl:       None, 1, 2

# Constraints (NumPy/Python)
IF [numpy] = 1.9  THEN [python] in {2.7, 3.4};
IF [numpy] = 1.10 THEN [python] in {2.7, 3.4};
IF [numpy] = 1.11 THEN [python] in {2.7, 3.4, 3.5};
IF [numpy] = 1.12 THEN [python] in {2.7, 3.4, 3.5, 3.6};
IF [numpy] = 1.13 THEN [python] in {2.7, 3.4, 3.5, 3.6};
IF [numpy] = 1.14 THEN [python] in {2.7, 3.4, 3.5, 3.6};

# Constraints (iDeep/Python)
IF [ideep] <> "None" THEN [python] in {2.7, 3.5, 3.6};

# Constraints (iDeep/NumPy)
IF [ideep] <> "None" THEN [numpy] in {1.13, 1.14};

# Constraints (CUDA/cuDNN)
IF [cuda] = 7.0 THEN [cudnn] in {"None", "4"};
IF [cuda] = 7.5 THEN [cudnn] in {"None", "4", "5", "5.1", "6", "7"};
IF [cuda] = 8.0 THEN [cudnn] in {"None", "5", "5.1", "6", "7"};
IF [cuda] = 9.0 THEN [cudnn] in {"None", "7"};
IF [cuda] = 9.1 THEN [cudnn] in {"None", "7"};

# Constraints (CUDA/NCCL)
IF [cuda] = 7.0 THEN [nccl] in {"None"};
IF [cuda] = 7.5 THEN [nccl] in {"None", "1"};
IF [cuda] = 8.0 THEN [nccl] in {"None", "1", "2"};
IF [cuda] = 9.0 THEN [nccl] in {"None", "1", "2"};
IF [cuda] = 9.1 THEN [nccl] in {"None", "1", "2"};
'''


###
### Model Definition (for Tool API)
###

_test_axes = [
    ('base',    ['ubuntu14', 'ubuntu16', 'centos6', 'centos7']),
    ('python',  ['2.7', '3.4', '3.5', '3.6']),
    ('numpy',   ['1.9', '1.10', '1.11', '1.12', '1.13', '1.14']),
    ('scipy',   ['None', '0.19']),
    ('ideep',   ['None', '1.0.4']),
    ('cuda',    ['7', '7.5', '8.0', '9.0', '9.1']),
    ('cudnn',   ['None', '4', '5', '5.1', '6', '7']),
    ('nccl',    ['None', '1', '2']),
]


def _validate_numpy_python(numpy, python):
    valid = []
    if numpy == '1.9':
        valid = ['2.7', '3.4']
    elif numpy == '1.10':
        valid = ['2.7', '3.4']
    elif numpy == '1.11':
        valid = ['2.7', '3.4', '3.5']
    elif numpy == '1.12':
        valid = ['2.7', '3.4', '3.5', '3.6']
    elif numpy == '1.13':
        valid = ['2.7', '3.4', '3.5', '3.6']
    elif numpy == '1.14':
        valid = ['2.7', '3.4', '3.5', '3.6']
    return python in valid


def _validate_ideep_python(ideep, python):
    return ideep == 'None' or python in ['2.7', '3.5', '3.6']


def _validate_ideep_numpy(ideep, numpy):
    return ideep == 'None' or numpy in ['1.13', '1.14']


def _validate_cuda_cudnn(cuda, cudnn):
    valid_cudnns = ['None']

    if cuda == '7':
        valid_cudnns += ['4']
    elif cuda == '7.5':
        valid_cudnns += ['4', '5', '5.1', '6', '7']
    elif cuda == '8.0':
        valid_cudnns += ['5', '5.1', '6', '7']
    elif cuda == '9.0':
        valid_cudnns += ['7']
    elif cuda == '9.1':
        valid_cudnns += ['7']

    return cudnn in valid_cudnns


def _validate_cuda_nccl(cuda, nccl):
    valid_nccls = ['None']

    if cuda == '7':
        pass
    elif cuda == '7.5':
        valid_nccls += ['1']
    elif cuda == '8.0':
        valid_nccls += ['1', '2']
    elif cuda == '9.0':
        valid_nccls += ['1', '2']
    elif cuda == '9.1':
        valid_nccls += ['1', '2']

    return nccl in valid_nccls



def assert_dict_set_equal(self, ds1, ds2):
    self.assertEqual(
        sorted([d.items() for d in ds1]),
        sorted([d.items() for d in ds2]),
    )


class TestFromDict(unittest.TestCase):
    def test_usecase(self):
        begin = datetime.now()
        api_cases = list(from_dict(
                        dict(_test_axes),
                        compose_filter_funcs(
                            _validate_numpy_python,
                            _validate_ideep_python,
                            _validate_ideep_numpy,
                            _validate_cuda_cudnn,
                            _validate_cuda_nccl,
                        ), random_seed=1))
        print('from_dict: {}'.format(datetime.now() - begin))

        begin = datetime.now()
        cmd_cols, cmd_rows = list(from_model(_model))
        print('from_model: {}'.format(datetime.now() - begin))

        cmd_cases = [dict(zip(cmd_cols, r)) for r in cmd_rows]
        assert_dict_set_equal(self, api_cases, cmd_cases)


class TestProduct(unittest.TestCase):
    def test_simple(self):
        assert_dict_set_equal(self, [
            {'x': 10, 'y': 'a'},
            {'x': 10, 'y': 'b'},
            {'x': 10, 'y': 'c'},
            {'x': 20, 'y': 'a'},
            {'x': 20, 'y': 'b'},
            {'x': 20, 'y': 'c'},
        ], product({'x': [10, 20], 'y': ['a', 'b', 'c']}))


class TestPopulateExclusionRules(unittest.TestCase):
    def test_simple(self):
        def filter_func(p1, p2):
            self.assertFalse(p1 == True and p2 == True)
            return p1 == True or p2 == True

        params = {
            'p1': [True, False],
            'p2': [True, False],
            'p3': [True, False],
        }
        initial_rules = [
            {'p1': True, 'p2': True},
            {'p1': True, 'p2': True, 'p3': True}
        ]
        final_rules = _populate_exclusion_rules(
            params, compose_filter_funcs(filter_func), initial_rules)
        expected_rules = [
            {'p1': True, 'p2': True},
            {'p1': True, 'p2': True, 'p3': True},
            {'p1': False, 'p2': False},
        ]
        assert_dict_set_equal(self, expected_rules, final_rules)
