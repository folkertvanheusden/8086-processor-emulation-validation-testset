#! /usr/bin/python3

from flags import parity, flags_or, flags_and, flags_xor
from helpers import emit_header, emit_tail, emit_tail_fail
from values_16b import get_pairs_16b
import sys

p = sys.argv[1]

n = 0
fh = None

def emit_test(v1, v2, mode, target, instr):
    global n
    global fh

    if (n % 512) == 0:
        if fh != None:
            emit_tail(fh)

            fh.close()

        fh = None

    if fh == None:
        file_name = f'or_xor_and_test_16b_{n}.asm'

        fh = open(p + '/' + file_name, 'w')

        emit_header(fh)

    label = f'test_{v1:x}_{v2:x}_{instr}_{n}'

    fh.write(f'{label}:\n')

    # reset flags
    fh.write(f'\txor ax,ax\n')
    fh.write(f'\tpush ax\n')
    fh.write(f'\tpopf\n')

    target_use_name = 'ax' if target else 'dx'

    # verify value
    fh.write(f'\tmov {target_use_name},#${v1:04x}\n')

    if mode != 3:
        fh.write(f'\tmov bx,#${v2:04x}\n')
    
    # do test
    if mode == 0:
        if instr == 0:
            fh.write(f'\tor {target_use_name},bx\n')
            (check_val, flags) = flags_or(v1, v2, True)

        elif instr == 1:
            fh.write(f'\txor {target_use_name},bx\n')
            (check_val, flags) = flags_xor(v1, v2, True)

        elif instr == 2:
            fh.write(f'\tand {target_use_name},bx\n')
            (check_val, flags) = flags_and(v1, v2, True)

        elif instr == 3:
            fh.write(f'\ttest {target_use_name},bx\n')
            (dummy, flags) = flags_and(v1, v2, True)
            check_val = v1

    elif mode == 1:
        fh.write(f'\tjmp skip_{label}_field\n')
        fh.write(f'{label}_field:\n')
        fh.write(f'\tdw 0\n')
        fh.write(f'skip_{label}_field:\n')
        fh.write(f'\tmov [{label}_field],bx\n')

        if instr == 0:
            fh.write(f'\tor {target_use_name},[{label}_field]\n')
            (check_val, flags) = flags_or(v1, v2, True)

        elif instr == 1:
            fh.write(f'\txor {target_use_name},[{label}_field]\n')
            (check_val, flags) = flags_xor(v1, v2, True)

        elif instr == 2:
            fh.write(f'\tand {target_use_name},[{label}_field]\n')
            (check_val, flags) = flags_and(v1, v2, True)

        elif instr == 3:
            fh.write(f'\ttest {target_use_name},[{label}_field]\n')
            (dummy, flags) = flags_and(v1, v2, True)
            check_val = v1

    elif mode == 2:
        fh.write(f'\tjmp skip_{label}_field\n')
        fh.write(f'{label}_field:\n')
        fh.write(f'\tdw 0\n')
        fh.write(f'skip_{label}_field:\n')
        fh.write(f'\tmov [{label}_field],{target_use_name}\n')

        if instr == 0:
            fh.write(f'\tor [{label}_field],bx\n')
            (check_val, flags) = flags_or(v1, v2, True)

        elif instr == 1:
            fh.write(f'\txor [{label}_field],bx\n')
            (check_val, flags) = flags_xor(v1, v2, True)

        elif instr == 2:
            fh.write(f'\tand [{label}_field],bx\n')
            (check_val, flags) = flags_and(v1, v2, True)

        elif instr == 3:
            fh.write(f'\ttest [{label}_field],bx\n')
            (dummy, flags) = flags_and(v1, v2, True)
            check_val = v1

        fh.write(f'\tmov {target_use_name},[{label}_field]\n')

    else:
        if instr == 0:
            fh.write(f'\tor {target_use_name},#${v2:02x}\n')
            (check_val, flags) = flags_or(v1, v2, True)

        elif instr == 1:
            fh.write(f'\txor {target_use_name},#${v2:02x}\n')
            (check_val, flags) = flags_xor(v1, v2, True)

        elif instr == 2:
            fh.write(f'\tand {target_use_name},#${v2:02x}\n')
            (check_val, flags) = flags_and(v1, v2, True)

        elif instr == 3:
            fh.write(f'\ttest {target_use_name},#${v2:02x}\n')
            (dummy, flags) = flags_and(v1, v2, True)
            check_val = v1

    fh.write(f'\tmov cx,#${check_val:02x}\n')

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

    fh.write(f'next_{label}:\n')
    fh.write('\n')

    n += 1

for mode in range(0, 4):
    for target in (False, True):
        for instr in range(0, 4):
            for pair in get_pairs_16b():
                emit_test(pair[0], pair[1], mode, target, instr)

if fh != None:
    emit_tail(fh)

    fh.close()
