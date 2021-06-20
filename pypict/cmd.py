import csv
import io
import os
import subprocess
import tempfile

from typing import Any, Iterable, Optional, Tuple

import pypict.capi


_PICT = 'pict'


def _get_pict_command() -> str:
    pictcmd = os.path.join(os.path.dirname(__file__), _PICT)
    if os.path.exists(pictcmd):
        return pictcmd
    return _PICT


def _pict(
        model_file: str,
        order: Optional[int] = None,
        random_seed: Optional[int] = None,
        *,
        use_subprocess: bool = True) -> str:
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


def from_model(
        model: str,
        *,
        use_subprocess: bool = False,
        **kwargs: Any) -> Tuple[Iterable[str], Iterable[Iterable[str]]]:
    with tempfile.NamedTemporaryFile() as f:
        f.write(model.encode('utf-8'))
        f.flush()
        output = _pict(f.name, use_subprocess=use_subprocess, **kwargs)
    rows = [r for r in csv.reader(io.StringIO(output), delimiter='\t')]
    return rows[0], rows[1:]
