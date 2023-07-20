#! /usr/bin/python3

from helpers import emit_header
import sys

p = sys.argv[1]

fh = open(p + '/' + 'cbw_cwd.asm', 'w')

emit_header(fh)

for test_v in (0, 127, 128, 129, 255, 254):
    fh.write('\tmov ah, #123\n')
    fh.write(f'\tmov al, #{test_v}\n')
    fh.write('\tcbw\n')
    
    if test_v & 128:
        test_v |= 0xff00

    fh.write(f'\tcmp ax, #${test_v:04x}\n')
    label1 = f'test_1_{test_v & 0xff}'
    fh.write(f'\tjz {label1}\n')
    fh.write(f'\thlt\n')
    fh.write(f'{label1}:\n')

for test_v in (0, 127, 128, 129, 255, 254, 32766, 32767, 32768, 32769, 65535, 65534):
    fh.write('\tmov dx, #$aee5\n')
    fh.write(f'\tmov ax, #${test_v:04x}\n')
    fh.write('\tcwd\n')

    dx = 0xffff if test_v & 32768 else 0

    fh.write(f'\tcmp dx, #${dx:04x}\n')
    label2 = f'test_2_test_{test_v}'
    fh.write(f'\tjz {label2}\n')
    fh.write(f'\thlt\n')
    fh.write(f'{label2}:\n')

fh.write('\tmov ax,#$a5ee\n')
fh.write('\tmov si,ax\n')  # set si to 'finished successfully'
fh.write('\thlt\n')
fh.close()
