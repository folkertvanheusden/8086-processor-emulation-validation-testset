#! /usr/bin/python3

from flags import parity, flags_cmp16
from helpers import emit_header, emit_tail, emit_tail_fail
from values_16b import get_pairs_16b
import sys

p = sys.argv[1]

fh = None
n_tests = 0

nr = 0

def emit_test(v1, v2, carry):
    global fh
    global n_tests

    for instr in range(0, 3):
        if fh == None:
            file_name = f'cmp16_{n_tests}.asm'
            fh = open(p + '/' + file_name, 'w')

            emit_header(fh)

        # test itself
        label = f'test_{instr}_{v1:04x}_{v2:04x}_{carry}'

        fh.write(f'{label}:\n')

        # reset flags
        fh.write(f'\txor ax,ax\n')
        fh.write(f'\tpush ax\n')
        fh.write(f'\tpopf\n')

        flags = flags_cmp16(carry, v1, v2)

        # to aid debugging
        fh.write(f'\tmov dx,#${n_tests:04x}\n')

        # verify value
        fh.write(f'\tmov ax,#${v1:04x}\n')

        if instr != 2:
            fh.write(f'\tmov bx,#${v2:04x}\n')
        
        if carry:
            fh.write('\tstc\n')

        else:
            fh.write('\tclc\n')

        # do test
        if instr == 0:
            fh.write(f'\tcmp ax,bx\n')

        elif instr == 1:
            fh.write(f'\tjmp skip_{label}_field\n')
            fh.write(f'{label}_field:\n')
            fh.write(f'\tdw 0\n')
            fh.write(f'skip_{label}_field:\n')
            fh.write(f'\tmov [{label}_field],bx\n')

            fh.write(f'\tcmp ax,[{label}_field]\n')

        else:
            fh.write(f'\tcmp ax,#${v2:04x}\n')

        # keep flags
        fh.write(f'\tpushf\n')

        fh.write(f'\tcmp ax,#${v1:04x}\n')
        fh.write(f'\tjz ok_{label}\n')
        emit_tail_fail(fh)

        # verify flags
        fh.write(f'ok_{label}:\n')
        fh.write(f'\tpop ax\n')
        fh.write(f'\tand ax,#$0fff\n')
        fh.write(f'\tcmp ax,#${flags:04x}\n')
        fh.write(f'\tjz next_{label}\n')
        emit_tail_fail(fh)

        # TODO: verify flags
        fh.write(f'next_{label}:\n')
        fh.write('\n')

        n_tests += 1

        if (n_tests % 512) == 0:
            emit_tail(fh)

            fh.close()
            fh = None

for carry in (False, True):
    for pair in get_pairs_16b():
        emit_test(pair[0], pair[1], carry)

emit_tail(fh)
fh.close()
