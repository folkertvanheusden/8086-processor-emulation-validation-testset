#! /usr/bin/python3

from flags import parity, flags_add_sub_cp
from helpers import emit_header, emit_tail, emit_tail_fail
import sys

p = sys.argv[1]

fh = None

n = 0

for al in range(0, 256):
   for val_mode in range(0, 2):
        for carry in (False, True):
            for val in range(0, 256):
                for instr in range(0, 4):
                    if (n % 512) == 0:
                        if fh != None:
                            emit_tail(fh)

                            fh.close()

                        fh = None

                    if fh == None:
                        file_name = f'adc_add_sbb_sub_{n}.asm'

                        fh = open(p + '/' + file_name, 'w')

                        emit_header(fh)

                    label = f'test_{al:02x}_{val:02x}_{carry}_{instr}_{val_mode}'

                    fh.write(f'{label}:\n')

                    fh.write(f'\tmov dx,#${n & 0xffff:04x}\n')
                    n += 1

                    # reset flags
                    fh.write(f'\txor ax,ax\n')
                    fh.write(f'\tpush ax\n')
                    fh.write(f'\tpopf\n')

                    (check_val, flags) = flags_add_sub_cp(instr >= 2, True if carry and (instr == 0 or instr == 2) else False, al, val)

                    # verify value
                    fh.write(f'\tmov al,#${al:02x}\n')
                    if val_mode == 0:
                        fh.write(f'\tmov bl,#${val:02x}\n')
                        add_name = 'bl'
                    else:
                        add_name = f'#${val:02x}'
                    fh.write(f'\tmov cl,#${check_val:02x}\n')
                    
                    if carry:
                        fh.write('\tstc\n')

                    else:
                        fh.write('\tclc\n')

                    # do test
                    if instr == 0:
                        fh.write(f'\tadc al,{add_name}\n')

                    elif instr == 1:
                        fh.write(f'\tadd al,{add_name}\n')

                    elif instr == 2:
                        fh.write(f'\tsbb al,{add_name}\n')

                    elif instr == 3:
                        fh.write(f'\tsub al,{add_name}\n')

                    # keep flags
                    fh.write(f'\tpushf\n')

                    fh.write(f'\tcmp al,cl\n')
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
