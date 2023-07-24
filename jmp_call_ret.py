#! /usr/bin/python3

from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'jmp_call_ret.asm', 'w')

emit_header(fh)

fh.write(
'''
; JMP NEAR
test_001:
    mov si,#$0001
    jmp test_001a_ok
    hlt
test_001a_ok:

; CALL NEAR
test_002:
    mov si,#$0002
    call test_002_sub
    jmp test_002_ok
    hlt
test_002_sub:
    ret
    hlt
test_002_ok:
    jmp test_003

; jump while dereferencing dw containing target address
test_003_data:
    dw test_003_ok
test_003:
    mov si,#$0003
    jmp [test_003_data]
    hlt
test_003_ok:
    jmp test_004

; call while dereferencing dw containing target address
test_004_data:
    dw test_004_sub
test_004:
    mov si,#$0004
    call [test_004_data]
    jmp test_004_ok
    hlt
test_004_sub:
    ret
    hlt
test_004_ok:

; retn
test_005:
    mov si,#$0004
    mov ax,sp
    push si
    push ax
    push ax
    push ax
    call test_005_sub
    jmp test_005_cont
test_005_sub:
    ret 6
test_005_cont:
    pop bx
    cmp bx,#$0004
    jz test_005_contb
    hlt
test_005_contb:
    cmp ax,sp
    jz test_005_ok
    hlt
test_005_ok:

finish:
''')

emit_tail(fh)

fh.close()
