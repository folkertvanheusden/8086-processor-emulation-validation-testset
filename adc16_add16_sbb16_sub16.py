#! /usr/bin/python3

from flags import parity, flags_add_sub_cp16
from helpers import emit_header, emit_tail, emit_tail_fail
from values_16b import get_pairs_16b
import sys

p = sys.argv[1]

fh = None
n_tests = 0

def emit_test(instr, v1, v2, carry, from_mode, target):
    global fh
    global n_tests

    if from_mode == 2 and target == 2:
        return

    if fh == None:
        file_name = f'adc16_add16_{n_tests}.asm'
        fh = open(p + '/' + file_name, 'w')

        emit_header(fh)

    # test itself
    label = f't_{n_tests}_{instr}_{v1:04x}_{v2:04x}_{carry}_{from_mode}_{target}'

    fh.write(f'{label}:\n')

    fh.write(f'\tmov si,#${n_tests:04x}\n')

    # reset flags
    fh.write(f'\txor ax,ax\n')
    fh.write(f'\tpush ax\n')
    fh.write(f'\tpopf\n')

    (check_val, flags) = flags_add_sub_cp16(instr >= 2, True if carry and (instr == 0 or instr == 2) else False, v1, v2)

    if target == 0:
        target_use_name = 'dx'
    elif target == 1:
        target_use_name = 'ax'
    elif target == 2:
        fh.write(f'\tjmp skip_{label}_field_to\n')
        fh.write(f'{label}_field_to:\n')
        fh.write(f'\tdw 0\n')
        fh.write(f'skip_{label}_field_to:\n')

        target_use_name = f'[{label}_field_to]'

    # verify value
    fh.write(f'\tmov {target_use_name},#${v1:04x}\n')  # initialize target
    if from_mode != 1:
        fh.write(f'\tmov bx,#${v2:04x}\n')  # initialize value that will be adc/add/etc'd
    fh.write(f'\tmov cx,#${check_val:04x}\n')  # register that will contain the result
    
    if carry:
        fh.write('\tstc\n')

    else:
        fh.write('\tclc\n')

    if from_mode == 0:
        from_use_name = 'bx'

    elif from_mode == 1:
        from_use_name = f'#${v2:04x}'

    elif from_mode == 2:
        fh.write(f'\tjmp skip_{label}_field\n')
        fh.write(f'{label}_field:\n')
        fh.write(f'\tdw 0\n')
        fh.write(f'skip_{label}_field:\n')
        fh.write(f'\tmov [{label}_field],bx\n')

        from_use_name = f'[{label}_field]'

    # do test
    if instr == 0:
        fh.write(f'\tadc {target_use_name},{from_use_name}\n')

    elif instr == 1:
        fh.write(f'\tadd {target_use_name},{from_use_name}\n')

    elif instr == 2:
        fh.write(f'\tsbb {target_use_name},{from_use_name}\n')

    elif instr == 3:
        fh.write(f'\tsub {target_use_name},{from_use_name}\n')

    # keep flags
    fh.write(f'\tpushf\n')

    fh.write(f'\tcmp {target_use_name},cx\n')
    fh.write(f'\tjz ok_{label}\n')

    emit_tail_fail(fh)

    fh.write(f'ok_{label}:\n')

    # verify flags
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

for instr in range(0, 4):
    for target in (0, 1, 2):
        for carry in (False, True):
            for from_mode in (0, 1, 2):
                for pair in get_pairs_16b():
                    emit_test(instr, pair[0], pair[1], carry, from_mode, target)

emit_tail(fh)
fh.close()
