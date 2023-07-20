#! /usr/bin/python3

from helpers import emit_header
import sys

p = sys.argv[1]

fh = open(p + '/' + 'misc2.asm', 'w')

emit_header(fh)

fh.write(
'''
test_01a:
    mov si,#$001a
    mov ax,#test_01a_continue0
    push ax
    ret
    hlt
    org $2000
test_01a_continue0:
    mov ax,#$300
    push cs
    mov cs,ax
    org $3000
test_01a_continue1:
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    pop dx
    cmp dx,#$0000
    beq test_01a_continue2
    hlt
test_01a_continue2:
    ;
    nop

finish:
''')

fh.write('\tmov ax,#$a5ee\n')
fh.write('\tmov si,ax\n')  # set si to 'finished successfully'
fh.write('\thlt\n')
fh.close()
