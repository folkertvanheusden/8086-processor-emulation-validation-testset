#! /usr/bin/python3

from flags import parity, flags_inc_dec16
from helpers import emit_header, emit_tail
from values_16b import b16_values
import sys

p = sys.argv[1]

fh = None
n_tests = 0

nr = 0

def emit_test(v1, carry):
    global fh
    global n_tests

    for instr in range(0, 2):
        if fh == None:
            file_name = f'cmp16_{n_tests}.asm'
            fh = open(p + '/' + file_name, 'w')

            emit_header(fh)

        # test itself
        label = f'test_{instr}_{v1:04x}_{carry}'

        fh.write(f'{label}:\n')

        # reset flags
        fh.write(f'\txor ax,ax\n')
        fh.write(f'\tpush ax\n')
        fh.write(f'\tpopf\n')

        flags = flags_inc_dec16(carry, v1, instr == 1)

        # to aid debugging
        fh.write(f'\tmov dx,#${n_tests:04x}\n')

        # verify value
        fh.write(f'\tmov ax,#${v1:04x}\n')

        if carry:
            fh.write('\tstc\n')

            flags |= 1

        else:
            fh.write('\tclc\n')

        # do test
        if instr == 0:
            fh.write(f'\tinc ax\n')

            cmp_val = (v1 + 1) & 0xffff

        elif instr == 1:
            fh.write(f'\tdec ax\n')

            cmp_val = (v1 - 1) & 0xffff

        # keep flags
        fh.write(f'\tpushf\n')

        fh.write(f'\tcmp ax,#${cmp_val:04x}\n')
        fh.write(f'\tjz ok_{label}\n')
        fh.write(f'\thlt\n')

        # verify flags
        fh.write(f'ok_{label}:\n')
        fh.write(f'\tpop ax\n')
        fh.write(f'\tcmp ax,#${flags:04x}\n')
        fh.write(f'\tjz next_{label}\n')
        fh.write(f'\thlt\n')

        # TODO: verify flags
        fh.write(f'next_{label}:\n')
        fh.write('\n')

        n_tests += 1

        if (n_tests % 512) == 0:
            emit_tail(fh)

            fh.close()
            fh = None

for carry in (False, True):
    for val in b16_values:
        emit_test(val, carry)

emit_tail(fh)
fh.close()
