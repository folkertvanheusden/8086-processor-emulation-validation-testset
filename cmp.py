#! /usr/bin/python3

from flags import parity, flags_cmp
from helpers import emit_header, emit_tail, emit_tail_fail
import sys

p = sys.argv[1]

nr = 0
fh = None

def emit_test(al, val, carry, instr):
    global fh
    global nr

    if fh == None:
        file_name = f'cmp_{al:x}_{val:x}_{nr}.asm'

        fh = open(p + '/' + file_name, 'w')

        emit_header(fh)

    label = f'test_{instr}_{al:02x}_{val:02x}_{carry}_{nr}'

    fh.write(f'{label}:\n')

    fh.write(f'\tmov si,#${nr & 0xffff:04x}\n')

    # reset flags
    fh.write(f'\txor ax,ax\n')
    fh.write(f'\tpush ax\n')
    fh.write(f'\tpopf\n')

    flags = flags_cmp(carry, al, val)

    # verify value
    fh.write(f'\tmov al,#${al:02x}\n')
    fh.write(f'\tmov bl,#${val:02x}\n')
    
    if carry:
        fh.write('\tstc\n')

    else:
        fh.write('\tclc\n')

    if instr >= 2:
        fh.write(f'\tmov [field_{label}],bl\n')

    # do test
    if instr == 0:
        fh.write(f'\tcmp al,bl\n')

    elif instr == 1:
        fh.write(f'\tcmp al,#${val:02x}\n')

    elif instr == 2:
        fh.write(f'\tcmp al,[field_{label}]\n')

    # keep flags
    fh.write(f'\tpushf\n')

    fh.write(f'\tcmp al,#${al:02x}\n')
    fh.write(f'\tjz ok_a_{label}\n')

    emit_tail_fail(fh)

    fh.write(f'ok_a_{label}:\n')

    fh.write(f'\tcmp bl,#${val:02x}\n')
    fh.write(f'\tjz ok_b_{label}\n')

    emit_tail_fail(fh)

    fh.write(f'ok_b_{label}:\n')

    # verify flags
    fh.write(f'\tpop ax\n')
    fh.write(f'\tand ax,#$0fff\n')
    fh.write(f'\tcmp ax,#${flags:04x}\n')
    fh.write(f'\tjz next_{label}\n')
    emit_tail_fail(fh)

    if instr >= 2:
        fh.write(f'field_{label}:\n')
        fh.write(f'\tdw 0\n')
        fh.write(f'\tnop\n')
        fh.write(f'\tnop\n')

    fh.write(f'next_{label}:\n')
    fh.write('\n')

    nr += 1

    if (nr % 512) == 0:
        emit_tail(fh)

        fh.close()

        fh = None

for al in range(0, 256):
    for val in range(0, 256):
        for carry in range(0, 2):
            for instr in range(0, 3):
                emit_test(al, val, carry, instr)

if fh != None:
    emit_tail(fh)

    fh.close()
