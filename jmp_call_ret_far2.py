#! /usr/bin/python3

from helpers import emit_header, emit_tail, emit_tail_fail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'jmp_call_ret_far2_A.asm', 'w')

emit_header(fh)

fh.write(
'''
; CALL FAR
test_004:
    mov si,#$0004
    DB $9A ; opcode for call far
    DW $0  ; offset
    DW $1000 ; segment
''')

emit_tail(fh)

fh.close()

fh = open(p + '/' + 'jmp_call_ret_far2_B.asm', 'w')
fh.write('\tretf\n')
emit_tail_fail(fh)
fh.close()
