#! /usr/bin/python3

from flags import parity, flags_add_sub_cp
from helpers import emit_header, emit_tail, emit_tail_fail
import sys

p = sys.argv[1]

fh = None

n = 0

for al in range(0, 256):
    if (n % 512) == 0:
        if fh != None:
            emit_tail(fh)

            fh.close()

        fh = None

    if fh == None:
        file_name = f'neg_{n}.asm'

        fh = open(p + '/' + file_name, 'w')

        emit_header(fh)

    label = f'neg_{al:02x}'

    fh.write(f'{label}:\n')

    n += 1

    # reset flags
    fh.write(f'\txor ax,ax\n')
    fh.write(f'\tpush ax\n')
    fh.write(f'\tpopf\n')

    (check_val, flags) = flags_add_sub_cp(True, False, 0, al)

    neg_val = (-al) & 0xff

    flags &= ~1
    flags |= 1 if al != 0 else 0

    # verify value
    fh.write(f'\tmov al,#${al:02x}\n')
    fh.write('\tneg al\n')

    # keep flags
    fh.write(f'\tpushf\n')

    fh.write(f'\tcmp al,#${neg_val:02x}\n')
    fh.write(f'\tjz ok_{label}\n')

    emit_tail_fail(fh)

    fh.write(f'ok_{label}:\n')

    # verify flags
    fh.write(f'\tpop ax\n')
    fh.write(f'\tand ax,#$0fff\n')
    fh.write(f'\tcmp ax,#${flags:04x}\n')
    fh.write(f'\tjz next_{label}\n')
    emit_tail_fail(fh)

    fh.write(f'next_{label}:\n')
    fh.write('\n')

emit_tail(fh)

fh.close()
