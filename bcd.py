#! /usr/bin/python3

from flags import flags_add_sub_cp
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

            flag_c = True if temp_flags & 1 else False
            flag_a = True if temp_flags & 16 else False

            if (temp_al & 0x0f) > 9 or flag_a:
                temp_al += 6
                flag_c |= flag_a
            else:
                flag_a = False

            if (temp_al & 0xf0) > 0x90 or flag_c:
                temp_al += 0x60
                flag_c = True
            else:
                flag_c = False

            result_value = temp_al & 0xff

            result_flags = (temp_flags & ~(1 | 16)) | (flag_c << 0) | (flag_a << 4)

            fh.write(f'\tmov ax,#${temp_flags:02x}\n')
            fh.write(f'\tpush ax\n')
            fh.write(f'\tpopf\n')

            fh.write(f'\tmov al,#${al:02x}\n')
            fh.write(f'\tmov bl,#${bl:02x}\n')
            fh.write(f'\tadd al,bl\n')

            fh.write(f'\tdaa\n')

            fh.write(f'\tpushf\n')
            fh.write(f'\tpop cx\n')
            fh.write(f'\tand cx,#$fff\n')
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
