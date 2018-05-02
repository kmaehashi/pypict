import csv
import io
import subprocess
import tempfile


def _pict(model_file, order=None, random_seed=None):
    # TODO: support more options
    cmdline = ['pict', model_file]
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
