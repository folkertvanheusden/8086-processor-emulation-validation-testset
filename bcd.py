#! /usr/bin/python3

from flags import parity, flags_add_sub_cp
from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = None
n = 0

for carry in range(0, 2):
    for al in range(0, 0x100):
        if (al & 0x0f) > 9 or (al & 0xf0) > 0x90:
            continue

        for bl in range(0, 0x100):
            if (bl & 0x0f) > 9 or (bl & 0xf0) > 0x90:
                continue

            if fh == None:
                fh = open(p + '/' + f'bcd_{n}.asm', 'w')

                emit_header(fh)

            label = f'test_{al:02x}_{bl:02x}_'

            (temp_al, temp_flags) = flags_add_sub_cp(False, True if carry else False, al, bl)

            old_temp_al = temp_al

            flag_c = True if temp_flags & 1 else False
            flag_a = True if temp_flags & 16 else False
            old_flag_c = flag_c
            old_flag_a = flag_a

            if (temp_al & 0x0f) > 9 or flag_a:
                new_flag_a = (temp_al & 0x0f) + 6 > 9
                temp_al += 6

                flag_c = old_flag_c or new_flag_a

                flag_a = True
            else:
                flag_a = False

            if (old_temp_al & 0xf0) > 0x90 or old_flag_c:
                temp_al += 0x60
                flag_c = True
            else:
                flag_c = False

            result_value = temp_al & 0xff

            result_flags = (temp_flags & ~(1 | 4 | 16 | 64 | 128)) | (1 if flag_c else 0) | (16 if flag_a else 0)

            if parity(result_value):
                result_flags |= 4  # parity

            if result_value == 0:
                result_flags |= 64  # zero

            if result_value & 128:
                result_flags |= 128

            fh.write(f'\tmov ax,#${temp_flags:02x}\n')
            fh.write(f'\tpush ax\n')
            fh.write(f'\tpopf\n')

            fh.write(f'\tmov al,#${al:02x}\n')
            fh.write(f'\tmov bl,#${bl:02x}\n')
            fh.write(f'\tadd al,bl\n')

            fh.write(f'\tdaa\n')

            fh.write(f'\tpushf\n')
            fh.write(f'\tpop cx\n')
            # overflow flag is undefined
            fh.write(f'\tand cx,#$7ff\n')
            fh.write(f'\tcmp cx,#${result_flags:02x}\n')
            fh.write(f'\tjz {label}_3_ok\n')
            fh.write(f'\thlt\n')
            fh.write(f'\t{label}_3_ok:\n')

            fh.write(f'\t; check result of daa\n')
            fh.write(f'\tcmp al,#${result_value:02x}\n')
            fh.write(f'\tjz {label}_4_ok\n')
            fh.write(f'\thlt\n')
            fh.write(f'\t{label}_4_ok:\n')

            n += 1

            if (n % 512) == 0:
                emit_tail(fh)
                fh.close()

                fh = None

if fh != None:
    emit_tail(fh)

    fh.close()
