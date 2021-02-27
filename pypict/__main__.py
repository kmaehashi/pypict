import sys

import pypict.capi


if __name__ == '__main__':
    sys.stdout.write(pypict.capi.execute(sys.argv[1:]))
