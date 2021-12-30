#!/bin/bash -uex

# Build wheels using manylinux1 Docker image provided by PyPA:
# https://github.com/pypa/manylinux

PKG_DIR="$(cd "$(dirname $0)"; pwd)"

function run_manylinux() {
  docker run \
    --rm \
    --user $(id -u):$(id -g) \
    --volume "${PKG_DIR}:/package" \
    --workdir /package \
    quay.io/pypa/manylinux1_x86_64 \
    "$@"
}

rm -rf dist wheelhouse
for PYTHON in cp37-cp37m cp38-cp38 cp39-cp39 cp310-cp310; do
  run_manylinux sh -uex -c "
export PATH=/opt/python/${PYTHON}/bin:\${PATH}
export HOME=/tmp
export LD_LIBRARY_PATH=\${PWD}/pict:\${LD_LIBRARY_PATH}

pip install --user 'Cython==0.29.26'
rm -rf dist
python setup.py build_pict test bdist_wheel

auditwheel --verbose repair dist/*-*-${PYTHON}-linux_x86_64.whl
"
done
