#! /usr/bin/python3

from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'misc2.asm', 'w')

emit_header(fh)

fh.write(
'''
test_019:
    mov si,#$0019
    mov ax,#test_019_continue0
    push ax
    ret
    hlt
    org $2000
test_019_continue0:
    mov ax,#$100
    jmp mov_cs
mov_cs:
    mov cs,ax
    ; clear queue
    jmp mov_cs
    hlt
    org $3000
test_019_continue1:
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    ;
    nop

finish:
''')

emit_tail(fh)

fh.close()
