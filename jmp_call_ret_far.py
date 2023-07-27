#! /usr/bin/python3

from helpers import emit_header, emit_tail, emit_tail_fail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'jmp_call_ret_far_A.asm', 'w')

emit_header(fh)

fh.write(
'''
; JMP FAR
test_003:
    mov si,#$0003
    DB $EA ; opcode for jump far
    DW $0  ; offset
    DW $1000 ; segment
''')

emit_tail_fail(fh)

fh.close()

fh = open(p + '/' + 'jmp_call_ret_far_B.asm', 'w')
emit_tail(fh)
fh.close()
