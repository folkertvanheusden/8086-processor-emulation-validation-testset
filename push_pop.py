#! /usr/bin/python3

from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'push_pop.asm', 'w')

emit_header(fh)

fh.write('\tjmp skip\n')
fh.write('space:\n')
fh.write('\tdw 0\n')
fh.write('skip:\n')

some_value = 13
nr = 1

# TODO: DS, SP, CS, #....
for reg in 'AX', 'CX', 'DX', 'BX', 'BP', 'SI', 'DI', 'ES':
    # initialize test register
    some_value ^= nr * 131
    some_value &= 0xffff
    nr += 1

    fh.write(f'\tmov ax,#${some_value:04x}\n')
    if reg != 'AX':
        fh.write(f'\tmov {reg},ax\n')

    # do
    fh.write(f'\tpush {reg}\n')
    # verify that the push did not alter the register
    fh.write(f'\tmov ax,{reg}\n')
    fh.write(f'\tcmp ax,#${some_value:04x}\n')
    l0 = f'ok___{reg}'
    fh.write(f'\tjz {l0}\n')
    fh.write(f'\thlt\n')
    fh.write(f'{l0}:\n')

    # alter test-register
    fh.write(f'\tmov ax,#${(some_value ^ 0xffff) >> 1:04x}\n')
    if reg != 'AX':
        fh.write(f'\tmov {reg},ax\n')

    # stack contains expected value?
    fh.write(f'\tcmp $7fe,#${some_value:04x}\n')
    l1 = f'ok_a_{reg}'
    fh.write(f'\tjz {l1}\n')
    fh.write(f'\thlt\n')
    fh.write(f'{l1}:\n')

    # check if pop returns expected value
    fh.write(f'\tpop {reg}\n')
    if reg != 'AX':
        fh.write(f'\tmov ax,{reg}\n')
    fh.write(f'\tcmp ax,#${some_value:04x}\n')
    l2 = f'ok_b_{reg}'
    fh.write(f'\tjz {l2}\n')
    fh.write(f'\thlt\n')
    fh.write(f'{l2}:\n')

fh.write('\tjmp skip_dw_1\n')
fh.write('store_field:\n')
fh.write('\tdw 0\n')
fh.write('skip_dw_1:\n')
fh.write('\tmov ax,#$aa33\n')
fh.write('\tpush ax\n')
fh.write('\tpop [store_field]\n')
fh.write('\tmov ax,[store_field]\n')
fh.write('\tcmp ax,#$aa33\n')
fh.write('\tjz test_ok\n')
fh.write('\thlt\n')
fh.write('test_ok:\n')

fh.write('''
    mov bx,#$123
    mov cx,#$0000
    mov ds,bx
    push ds
    mov ds,cx
    pop ds
    mov ax,ds
    mov ds,cx
    cmp ax,#$123
    jz ds_test_1
    hlt
ds_test_1:
''')

# pop SP
fh.write('''
    jmp skip_dw_2
    dw $3321
skip_dw_2:
    mov bx,sp
    mov sp,#skip_dw_2
    pop sp
    mov ax,sp
    cmp ax,#$3321
    jnz pop_sp_fail
    hlt
pop_sp_fail:
    mov sp,bx
''')

# push SP
fh.write('''
    mov bx,sp
    push sp
    mov ax,sp
    mov di,ax
    cmp [di],bx
    jnz pop_sp_fail2
    hlt
pop_sp_fail2:
    pop sp
    cmp bx,sp
    jnz pop_sp_fail3
    hlt
pop_sp_fail3:
''')

# push/pop ss
fh.write('''
    ; adjust sp so that ss can be changed
    mov ax,sp
    sub ax,#$20
    mov sp,ax

    ; ss:sp now points to the previous location
    mov ax,#$2
    mov ss,ax

    push ss

    ; clear ss
    xor ax,ax
    mov ss,ax
    ; reset sp
    mov ax,sp
    add ax,#$20
    mov sp,ax

    pop ss

    mov ax,ss
    cmp ax,#$2
    jz ss_test_ok
    hlt
ss_test_ok:

    xor ax,ax
    mov ss,ax
''')

emit_tail(fh)

fh.close()
