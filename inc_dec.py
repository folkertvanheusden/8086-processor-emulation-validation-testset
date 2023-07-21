#! /usr/bin/python3

from flags import parity, flags_inc_dec
from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

prev_file_name = None
fh = None

for al in range(0, 256):
    file_name = f'inc_dec_{al:02x}.asm'

    if file_name != prev_file_name:

        prev_file_name = file_name

        if fh != None:
            emit_tail(fh)

            fh.close()

        fh = open(p + '/' + file_name, 'w')

        emit_header(fh)

    for carry in range(0, 2):
        for instr in range(0, 2):
            label = f'test_{instr}_{al:02x}_{carry}'

            fh.write(f'{label}:\n')

            # reset flags
            fh.write(f'\txor ax,ax\n')
            fh.write(f'\tpush ax\n')
            fh.write(f'\tpopf\n')

            flags = flags_inc_dec(carry, al, instr == 1)

            # verify value
            fh.write(f'\tmov al,#${al:02x}\n')
            
            if carry:
                fh.write('\tstc\n')
                flags |= 1  # !

            else:
                fh.write('\tclc\n')

            # do test
            if instr == 0:
                fh.write(f'\tinc al\n')
                cmp_val = (al + 1) & 0xff

            else:
                fh.write(f'\tdec al\n')
                cmp_val = (al - 1) & 0xff

            # keep flags
            fh.write(f'\tpushf\n')

            fh.write(f'\tcmp al,#${cmp_val:02x}\n')
            fh.write(f'\tjz ok_{label}\n')

            fh.write(f'\thlt\n')

            fh.write(f'ok_{label}:\n')

            # verify flags
            fh.write(f'\tpop ax\n')
            fh.write(f'\tand ax,#$0fff\n')
            fh.write(f'\tcmp ax,#${flags:04x}\n')
            fh.write(f'\tjz next_{label}\n')
            fh.write(f'\thlt\n')

            fh.write(f'next_{label}:\n')
            fh.write('\n')

emit_tail(fh)

fh.close()
