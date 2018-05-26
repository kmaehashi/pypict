import itertools

import pypict
from pypict.api import Task


def from_dict(params, filter_func=None, excludes=[], seeds=[],
              random_seed=None):
    """Generates pair-wise cases from given parameter dictionary."""

    if random_seed is None or isinstance(random_seed, int):
        return _from_dict(params, filter_func, excludes, seeds, random_seed)

    # Find the best (smallest) test suite by trying multiple seeds.
    best = None
    for rs in random_seed:
        case = _from_dict(params, filter_func, excludes, seeds, rs)
        if best is None or len(case) < len(best):
            best = case
    return best



def _from_dict(params, filter_func, excludes, seeds, random_seed):
    # Create PICT task.
    task = Task(seed=random_seed)

    # Parameter keys.
    keys = list(params.keys())

    # Generate exclusion rules from filter_func.
    if filter_func is not None:
        excludes = _populate_exclusion_rules(params, filter_func, excludes)

    # Build index of parameters.
    # idx2val[key][val_idx] -> val
    idx2val = {
        key: dict(enumerate(val))
        for key, val in params.items()
    }
    # val2idx[key][value] -> val_idx
    val2idx = {
        key: {val: val_idx for val_idx, val in validx2val.items()}
        for key, validx2val in idx2val.items()
    }
    # key_handle = key2handle[key]
    key2handle = {
        key: task.model.add_parameter(len(params[key]))
        for key in keys
    }

    # Register exclusion cases.
    for case in excludes:
        assert len(case) <= len(keys)
        task.add_exclusion([
            (key2handle[key], val2idx[key][val])
            for key, val in case.items()
        ])

    # Register seed cases.
    for case in seeds:
        assert len(case) == len(keys)
        task.model.add_seed([
            (key2handle[key], val2idx[key][val])
            for key, val in case.items()
        ])

    # Generate cases.
    for row in task.generate():
        yield {
            key: idx2val[key][val_idx]
            for key, val_idx in zip(keys, row)
        }


def compose_filter_funcs(*funcs):
    """Composes multiple filter functions.

    To accept the case, all functions must return True.
    """
    def _composed(combination):
        for func in funcs:
            accepted = True
            try:
                accepted = func(**combination)
            except TypeError:
                accepted = True
            if not accepted:
                return False
        return True
    return _composed


def product(params):
    """Generate product of parameters."""
    return [dict(zip(params.keys(), x))
            for x in itertools.product(*params.values())]


def _populate_exclusion_rules(params, filter_func, initial_rules=[]):
    rules = set([tuple(rule.items()) for rule in initial_rules])

    for r in range(1, len(params) + 1):
        # Pick r keys (1 <= r <= len(params)) from all parameter keys.
        for subkeys in itertools.combinations(params.keys(), r):
            # Generate cartesian product (i.e., full matrix) of parameter
            # values for the picked keys.
            # Then check if each parameter value set is excluded or not.
            for subvalue in itertools.product(*[params[k] for k in subkeys]):
                case = tuple(zip(subkeys, subvalue))
                if not case in rules and not filter_func(dict(case)):
                    # Need to add new rule to exclude the current case.
                    rules.add(case)
    return [dict(rule) for rule in rules]
