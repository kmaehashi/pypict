import csv
import io
import os
import subprocess
import sys
import tempfile

import pypict.capi


_PICT = 'pict'


def _get_pict_command():
    pictcmd = os.path.join(os.path.dirname(__file__), _PICT)
    if os.path.exists(pictcmd):
        return pictcmd
    return _PICT


def _pict(model_file, order=None, random_seed=None, *, use_subprocess=True):
    # TODO: support more options
    cmdline = [_get_pict_command(), model_file]
    if order is not None:
        cmdline += ['/o:{}'.format(order)]
    if random_seed is not None:
        cmdline += ['/r:{}'.format(random_seed)]

    if use_subprocess:
        return subprocess.check_output(cmdline).decode('utf-8')
    cmdline.pop(0)
    return pypict.capi.execute(cmdline)


def from_model(model, *, use_subprocess=False, **kwargs):
    with tempfile.NamedTemporaryFile() as f:
        f.write(model.encode('utf-8'))
        f.flush()
        output = _pict(f.name, use_subprocess=use_subprocess, **kwargs)
    rows = [r for r in csv.reader(io.StringIO(output), delimiter='\t')]
    return rows[0], rows[1:]
