#! /usr/bin/python3

from flags import parity, flags_add_sub_cp
from helpers import emit_header, emit_tail, emit_tail_fail
import sys

p = sys.argv[1]

fh = None
n = 0

# DAA
for carry in range(0, 2):
    for half_carry in range(0, 2):
        for in_al in range(0, 0x100):
            if fh == None:
                fh = open(p + '/' + f'bcd_daa_{n}.asm', 'w')

                emit_header(fh)

            label = f'test_{carry}_{half_carry}_{in_al:02x}_'

            flag_c = carry
            flag_a = half_carry

            before_flags = 2
            
            if flag_c:
                before_flags |= 1

            if flag_a:
                before_flags |= 16

            temp_al = in_al

            if (in_al & 0x0f) > 9 or flag_a:
                temp_al += 0x06
                temp_al &= 0xff

                flag_a = True

            # this configurable 'upper_nibble_check' comes from MartyPC
            upper_nibble_check = 0x9f if half_carry else 0x99

            if in_al > upper_nibble_check or flag_c:
                temp_al += 0x60
                temp_al &= 0xff

                flag_c = True

            result_value = temp_al

            result_flags = 2

            if flag_c:
                result_flags |= 1  # carry

            if parity(result_value):
                result_flags |= 4  # parity

            if flag_a:
                result_flags |= 16  # half carry

            if result_value == 0:
                result_flags |= 64  # zero

            if result_value & 128:
                result_flags |= 128  # sign

            fh.write(f'\tmov ax,#${before_flags:04x}\n')
            fh.write(f'\tpush ax\n')
            fh.write(f'\tpopf\n')

            fh.write(f'\tmov al,#${in_al:02x}\n')

            fh.write(f'\tdaa\n')

            fh.write(f'\tpush ax\n')

            fh.write(f'\tpushf\n')
            fh.write(f'\tpop cx\n')
            # overflow flag is undefined
            fh.write(f'\tand cx,#$7ff\n')
            fh.write(f'\tcmp cx,#${result_flags:04x}\n')
            fh.write(f'\tjz {label}_3_ok\n')
            emit_tail_fail(fh)
            fh.write(f'\t{label}_3_ok:\n')

            fh.write(f'\t; check result of daa\n')
            fh.write(f'\tpop ax\n')
            fh.write(f'\tcmp al,#${result_value:02x}\n')
            fh.write(f'\tjz {label}_4_ok\n')
            emit_tail_fail(fh)
            fh.write(f'\t{label}_4_ok:\n')

            n += 1

            if (n % 512) == 0:
                emit_tail(fh)
                fh.close()

                fh = None

if fh != None:
    emit_tail(fh)

    fh.close()


# BCD DAS
for carry in range(0, 2):
    for half_carry in range(0, 2):
        for in_al in range(0, 0x100):
            if fh == None:
                fh = open(p + '/' + f'bcd_das_{n}.asm', 'w')

                emit_header(fh)

            label = f'test_{carry}_{half_carry}_{in_al:02x}_'

            flag_c = carry
            flag_a = half_carry

            before_flags = 2
            
            if flag_c:
                before_flags |= 1

            if flag_a:
                before_flags |= 16

            temp_al = in_al

            flag_c = False

            if (in_al & 0x0f) > 9 or flag_a:
                temp_al -= 0x06
                temp_al &= 0xff

                flag_a = True

            # this configurable 'upper_nibble_check' comes from MartyPC
            upper_nibble_check = 0x9f if half_carry else 0x99

            if in_al > upper_nibble_check or carry:
                temp_al -= 0x60
                temp_al &= 0xff

                flag_c = True

            result_value = temp_al

            result_flags = 2

            if flag_c:
                result_flags |= 1  # carry

            if parity(result_value):
                result_flags |= 4  # parity

            if flag_a:
                result_flags |= 16  # half carry

            if result_value == 0:
                result_flags |= 64  # zero

            if result_value & 128:
                result_flags |= 128  # sign

            fh.write(f'\tmov ax,#${before_flags:04x}\n')
            fh.write(f'\tpush ax\n')
            fh.write(f'\tpopf\n')

            fh.write(f'\tmov al,#${in_al:02x}\n')

            fh.write(f'\tdas\n')

            fh.write(f'\tpush ax\n')

            fh.write(f'\tpushf\n')
            fh.write(f'\tpop cx\n')
            # overflow flag is undefined
            fh.write(f'\tand cx,#$7ff\n')
            fh.write(f'\tcmp cx,#${result_flags:04x}\n')
            fh.write(f'\tjz {label}_3_ok\n')

            emit_tail_fail(fh)

            fh.write(f'\t{label}_3_ok:\n')

            fh.write(f'\t; check result of daa\n')
            fh.write(f'\tpop ax\n')
            fh.write(f'\tcmp al,#${result_value:02x}\n')
            fh.write(f'\tjz {label}_4_ok\n')
            emit_tail_fail(fh)
            fh.write(f'\t{label}_4_ok:\n')

            n += 1

            if (n % 512) == 0:
                emit_tail(fh)
                fh.close()

                fh = None

if fh != None:
    emit_tail(fh)

    fh.close()
