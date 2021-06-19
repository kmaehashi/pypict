#!/bin/bash

set -uex

stubgen -m pypict.capi -o .
sed -i -e '/^def __pyx_/d' pypict/capi.pyi
