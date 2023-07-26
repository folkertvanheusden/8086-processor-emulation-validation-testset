#! /usr/bin/python3

from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'int.asm', 'w')

emit_header(fh)

fh.write(
'''
; DIV (3)
; divide by zero
test_001:
    mov si,#$0001
    jmp test_001_skip
test_001_word:
    dw 0
    nop
    nop
    nop
intvec_div3:
    mov bx,#$7777
    iret
test_001_skip:
    ; set interrupt vector
    mov ax,#intvec_div3
    mov [$0],ax
    ; this test set should fit in the first segment
    xor ax,ax
    mov [$2],ax
    ;
    ; will be set to 7777 by interrupt vector
    xor bx, bx
    ;
	mov ax,#0x4321
	mov dx,#0x8001
    ; this should invoke interrupt 0
	div [test_001_word]
    cmp bx,#$7777
    jz test_0019_ok
    hlt
test_0019_ok:
    cmp ax,#$e392
    jnz test_001a_ok
    hlt
test_001a_ok:

''')

for i in range(0x14, 0x100):
    fh.write(f'test_002_{i}:\n')

    vector_label = f'test_002_{i}_vec'
    fh.write(f'\tjmp skip_{vector_label}\n')
    fh.write(f'{vector_label}:\n')  # interrupt routine
    fh.write(f'\tmov dl,#{i}\n')
    fh.write(f'\tiret\n')
    fh.write(f'\n')
    fh.write(f'skip_{vector_label}:\n')
    fh.write(f'\tmov ax,#{vector_label}\n')  # set vector
    fh.write(f'\tmov [${i * 4 + 0:04x}],ax\n')  # ip
    fh.write(f'\txor ax,ax\n')
    fh.write(f'\tmov [${i * 4 + 2:04x}],ax\n')  # cs
    fh.write(f'\n')
    fh.write(f'\txor dx,dx\n')  # prepare
    fh.write(f'\tint {i}\n')  # invoke
    fh.write(f'\tcmp dx,#{i}\n')  # check
    fh.write(f'\tjz {vector_label}_ok\n')
    fh.write(f'\thlt\n')
    fh.write(f'{vector_label}_ok:\n')
    fh.write(f'\n')

emit_tail(fh)

fh.close()
