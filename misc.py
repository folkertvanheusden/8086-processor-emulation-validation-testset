#! /usr/bin/python3

from helpers import emit_header, emit_tail, get_tail_fail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'misc.asm', 'w')

emit_header(fh)

fh.write(f'''
; NOT
test_001:
    mov si,#$0001
    xor ax,ax
    mov bx,#$1234
    not bx
    cmp bx,#$EDCB
    jz test_001a_ok
    {get_tail_fail()}
test_001a_ok:

    cmp ax,#$0000

    jz test_001b_ok
    {get_tail_fail()}
test_001b_ok:

; MUL
test_002:
    mov si,#$0002
    xor ax,ax
    mov al,#$7f
    mov cl,#$fe
    mul cl
    cmp ax,#$7e02
    jz test_002_ok
    {get_tail_fail()}
test_002_ok:
; TODO: test flags

; MUL 16b
test_003:
    mov si,#$0003
    mov ax,#$1234
    mov cx,#$aa55
    mul cx
    cmp ax,#$9344
    jz test_003a_ok
    {get_tail_fail()}
test_003a_ok:
    cmp dx,#$0c1c
    jz test_003b_ok
    {get_tail_fail()}
test_003b_ok:
; TODO: test flags

; DIV
test_004:
    mov si,#$0004
	mov ax,#0x4321
	mov dx,#0x8001
	mov cx,#0x8fff
	div cx
    cmp ax,#$e392
    jz test_004a_ok
    {get_tail_fail()}
test_004a_ok:
    cmp dx,#$06b3
    jz test_004b_ok
    {get_tail_fail()}
test_004b_ok:
; NO(!) flags altered

; XCHG
test_005:
    mov si,#$0005
    pushf
	mov ax,#0x4321
	mov dx,#0x8001
    xchg ax,dx
    cmp ax,#0x8001
    jz test_005a_ok
    {get_tail_fail()}
test_005a_ok:
    cmp dx,#0x4321
    jz test_005b_ok
    {get_tail_fail()}
test_005b_ok:
    pushf
    pop bx
    pop ax
    cmp ax,bx
    jz test_005c_ok
    {get_tail_fail()}
test_005c_ok:

; CALL & RET
test_006:
    mov si,#$0006
    pushf
    pop bx
    mov ax,sp
    call test_006_sub_a
    jp test_006_cont
test_006_sub_a:
    pushf
    cmp ax,sp
    jne test_006_sub_a_ok
    {get_tail_fail()}
test_006_sub_a_ok:
    pop cx
    cmp bx,cx
    jz test_006_sub_b_ok
    {get_tail_fail()}
test_006_sub_b_ok:
    push bx
    popf
    ret
    {get_tail_fail()}
test_006_cont:
    cmp ax,sp
    jz test_006_b_ok
    {get_tail_fail()}
test_006_b_ok:
    pushf
    pop cx
    cmp bx,cx
    jz test_006_c_ok
    {get_tail_fail()}
test_006_c_ok:

test_007:
    mov si,#$0007
    mov bx,#$1234
    xor bx,bx
    cmp bx,#$0000
    jz test_007a_ok
    {get_tail_fail()}
test_007a_ok:

; DIV (2)
test_008:
    mov si,#$0008
    jmp test_008_skip
test_008_word:
    dw 0
    nop
    nop
    nop
test_008_skip:
	mov ax,#0x4321
	mov dx,#0x8001
	mov [test_008_word],#0x8fff
	div [test_008_word]
    cmp ax,#$e392
    jz test_008a_ok
    {get_tail_fail()}
test_008a_ok:

; MUL
test_009:
    mov si,#$0009
    jmp test_009_skip
test_009_byte:
    db 0
    nop
    nop
    nop
test_009_skip:
    xor ax,ax
    mov al,#$7f
    mov [test_009_byte],#$fe
    mul [test_009_byte]
    cmp ax,#$7e02
    jz test_009_ok
    {get_tail_fail()}
test_009_ok:
; TODO: test flags

; LDS
test_00a:
    mov si,#$000a
    jmp test_00a_skip
test_00a_words:
    dw $1234
    dw $6789
    nop
    nop
    nop
test_00a_skip:
    lds bx, [test_00a_words]
    cmp bx,#$1234
    jz test_00aa_ok
    {get_tail_fail()}
test_00aa_ok:
    mov dx,ds
    cmp dx,#$6789
    jz test_00ab_ok
    {get_tail_fail()}
test_00ab_ok:

; LES
test_00b:
    mov si,#$000b
    xor ax,ax
    mov ds,ax
    jmp test_00b_skip
test_00b_words:
    dw $3412
    dw $1219
    nop
    nop
    nop
test_00b_skip:
    les dx, [test_00b_words]
    cmp dx,#$3412
    jz test_00ba_ok
    {get_tail_fail()}
test_00ba_ok:
    mov bx,es
    cmp bx,#$1219
    jz test_00bb_ok
    {get_tail_fail()}
test_00bb_ok:

; INT
test_00c:
    jmp skip_int_func
int_func:
    mov cx,#$1726
    iret
skip_int_func:
    mov si,#$000c
    mov di,#$002a
    mov ax,#0
    mov [di],ax
    mov di,#$0028
    mov ax,#int_func
    mov [di],ax
    mov cx,#$4321
    int 10
    cmp cx,#$1726
    jz test_00c_ok
    {get_tail_fail()}
test_00c_ok:

; C flag
test_00d:
    xor ax,ax
    push ax
    popf
    ; set
    stc
    stc
    pushf
    pop ax
    and ax,#$1
    cmp ax,#$1
    jz test_00d_1
    {get_tail_fail()}
test_00d_1:
    ; invert
    stc
    cmc
    pushf
    pop ax
    and ax,#$1
    cmp ax,#$0
    jz test_00d_2
    {get_tail_fail()}
test_00d_2:
    ; set & reset
    stc
    clc
    pushf
    pop ax
    and ax,#$1
    cmp ax,#$0
    jz test_00d_3
    {get_tail_fail()}
test_00d_3:
    clc
    jnc test_00d_4
    {get_tail_fail()}
test_00d_4:
    stc
    jc test_00e
    {get_tail_fail()}

; XCHG2
test_value:
    dw $1234
test_00e:
    mov si,#$000e
    pushf
	mov ax,#$4321
    xchg ax,[test_value]
    pushf
    cmp ax,#$1234
    jz test_00ea_ok
    {get_tail_fail()}
test_00ea_ok:
    cmp [test_value],#$4321
    jz test_00eb_ok
    {get_tail_fail()}
test_00eb_ok:
    pop bx
    pop ax
    cmp ax,bx
    jz test_00ec_ok
    {get_tail_fail()}
test_00ec_ok:

test_00f:
    mov si,#$000f
    xor ax,ax
    push ax
    popf
    sti
    pushf
    pop ax
    and ax,#$200
    cmp ax,#$200
    jz test_00f_ok
    {get_tail_fail()}
test_00f_ok:

test_010:
    mov si,#$0010
    xor ax,ax
    push ax
    popf
    mov al,#$76
    add al,#$01
    jno test_010_1
    {get_tail_fail()}
test_010_1:
    add al,#$39
    jo test_010_2
    {get_tail_fail()}
test_010_2:

test_011:
    mov si,#$0011
    xor ax,ax
    push ax
    popf
    mov al,#$76
    mov bl,#$13
    cmp bl,al
    jl test_011_1
    {get_tail_fail()}
test_011_1:
    xchg bl,al
    cmp bl,al
    jnl test_011_2
    {get_tail_fail()}
test_011_2:

test_012:
    mov si,#$0012
    xor ax,ax
    push ax
    popf
    mov al,#$13
    mov bl,#$13
    cmp bl,al
    jle test_012_1
    {get_tail_fail()}
test_012_1:
    xchg bl,al
    cmp bl,al
    jnle test_012_2
    jmp test_012_2b
test_012_2:
    {get_tail_fail()}
test_012_2b:

test_013:
    mov si,#$0013
    mov ax,#$1234
    mov bp,ax
    mov bx,bp
    cmp bx,#$1234
    jz test_013_ok
    {get_tail_fail()}
test_013_ok:

test_014:
    mov si,#$0014
    xor ax,ax
    mov cl,al
    mov dl,al
    mov bl,al
    mov ch,#$12
    mov dh,#$34
    mov bh,#$56
    cmp cx,#$1200
    jz test_014_1_ok
    {get_tail_fail()}
test_014_1_ok:
    cmp dx,#$3400
    jz test_014_2_ok
    {get_tail_fail()}
test_014_2_ok:
    cmp bx,#$5600
    jz test_014_3_ok
    {get_tail_fail()}
test_014_3_ok:

test_015:
    mov si,#$0015
    mov bx,#$ae00
    mov cx,#$8e00
    mov dx,#$ce00
    cmp ch,#$8e
    jz test_015_1_ok
    {get_tail_fail()}
test_015_1_ok:
    cmp dh,#$ce
    jz test_015_2_ok
    {get_tail_fail()}
test_015_2_ok:
    cmp bh,#$ae
    jz test_015_3_ok
    {get_tail_fail()}
test_015_3_ok:

test_016:
    mov si,#$0016
    mov ax,cs
    cmp ax,#$0000
    jz test_016_ok
    {get_tail_fail()}
test_016_ok:

test_017:
    mov si,#$0017
    mov ax,ss
    cmp ax,#$0000
    jz test_017_ok
    {get_tail_fail()}
test_017_ok:

test_018:
    mov si,#$0018
; set $10000 to 12
    mov ax,#$1000
    mov ds,ax
    xor ax,ax
    mov di,ax
    mov [di],#$12
; check
    mov si,ax
    mov ax,#$5555
    dseg
    mov al,[si]
    cmp ax,#$5512
    jz test_018_ok
    {get_tail_fail()}
test_018_ok:
    xor ax,ax
    mov ds,ax
    jmp test_019_go

; NOT
test_019:
    dw $1234
test_019_go:
    mov si,#$0019
    xor ax,ax
    not [test_019]
    cmp [test_019],#$EDCB
    jz test_019a_ok
    {get_tail_fail()}
test_019a_ok:
    cmp ax,#$0000
    jz test_019b_ok
    {get_tail_fail()}
test_019b_ok:

; DIV
test_01a:
    mov si,#$001a
	mov ax,#0x4321
	mov dx,#0x8001
	mov cx,#0x004f
	div cl
    cmp ax,#$2ad9
    jz test_01a_ok
    {get_tail_fail()}
test_01a_ok:

; NOT
test_01b:
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $5678
    dw $1234
test_01b_go:
    mov si,#$001b

    ; NOT offset
    mov ax,#$0005
    ; ds is shifted 4 and then added so effectively this is an offset of $50
    mov ds,ax

    xor ax,ax
    not [test_01b]
    push ax
    ; ax is 0 here
    mov ds,ax

    ; CMP offset
    mov ax,#test_01b
    ; si = $1b here; $1b+$35 = $50
    add ax,#$35
    mov bp,ax

    cmp [bp + si],#$EDCB
    jz test_01ba_ok
    {get_tail_fail()}
test_01ba_ok:
    pop ax
    cmp ax,#$0000
    jz test_01bb_ok
    {get_tail_fail()}
test_01bb_ok:

finish:
''')

emit_tail(fh)

fh.close()
