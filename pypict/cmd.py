import csv
import io
import os
import subprocess
import tempfile


_PICT = 'pict'


def _get_pict_command():
    pictcmd = os.path.join(os.path.dirname(__file__), _PICT)
    if os.path.exists(pictcmd):
        return pictcmd
    return _PICT


def _pict(model_file, order=None, random_seed=None):
    # TODO: support more options
    cmdline = [_get_pict_command(), model_file]
    if order is not None:
        cmdline += ['/o:{}'.format(order)]
    if random_seed is not None:
        cmdline += ['/r:{}'.format(random_seed)]

    return subprocess.check_output(cmdline)


def from_model(model, **kwargs):
    with tempfile.NamedTemporaryFile() as f:
        f.write(model.encode('utf-8'))
        f.flush()
        output = _pict(f.name, **kwargs).decode('utf-8')
    rows = [r for r in csv.reader(io.StringIO(output), delimiter='\t')]
    return rows[0], rows[1:]
