#! /usr/bin/python3

from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'bcd.asm', 'w')

emit_header(fh)

# tests taken from the Intel documentation

# ADD AL, BL Before: AL=79H BL=35H EFLAGS(OSZAPC)=XXXXXX
# After: AL=AEH BL=35H EFLAGS(0SZAPC)=110000
# DAA Before: AL=AEH BL=35H EFLAGS(OSZAPC)=110000
# After: AL=14H BL=35H EFLAGS(0SZAPC)=X00111

# DAA Before: AL=2EH BL=35H EFLAGS(OSZAPC)=110000
# After: AL=04H BL=35H EFLAGS(0SZAPC)=X00101

fh.write(
'''
; daa test 1
    mov al,#$79
    mov bl,#$35
    add al,bl
    pushf

    ; check result of addition
    cmp al,#$ae
    beq test_1_1_ok
    hlt
test_1_1_ok:

    ; check flags of addition
    pop cx
    and cx,#$fff
    cmp cx,#$882
    beq test_1_2_ok
    hlt
test_1_2_ok:

    ;
    daa

    ; check flags of daa
    pushf
    pop cx
    and cx,#$fff
    cmp cx,#$17
    beq test_1_3_ok
    hlt
test_1_3_ok:

    cmp al,#$14
    beq test_1_4_ok
    hlt
test_1_4_ok:

; daa test 2
    ; setup flags
    mov ax,#$882
    push ax;
    popf
    ; do
    mov al,#$2e
    daa
    pushf
    ; verify outcome value
    cmp al,#$04
    beq test_2_1_ok
    hlt
test_2_1_ok:
    ; verify outcome flags
    pop ax
    and ax,#$fff
    cmp ax,#$b
    beq test_2_2_ok
    hlt
test_2_2_ok:

finish:
''')

emit_tail(fh)

fh.close()
