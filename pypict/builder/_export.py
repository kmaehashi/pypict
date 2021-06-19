from pypict import builder


def _literal(v):
    if isinstance(v, builder.Parameter):
        return f'[{v._name}]'
    elif isinstance(v, str):
        return f'"{v}"'  # TODO check?
    else:
        return str(v)


def _ValueSet(values):
    return '{ ' + ','.join([_literal(x) for x in values]) + ' }'
