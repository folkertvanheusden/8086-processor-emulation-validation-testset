#! /usr/bin/python3

from helpers import emit_header, emit_tail, get_tail_fail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'misc3.asm', 'w')

emit_header(fh)

fh.write(f'''
test_001:
    mov si,#$0001
    jmp test_001_do

test_001_source:
    dw $1234
    dw $5678
    dw $9abc
    dw $def0

test_001_dest:
    dw 0
    dw 0
    dw 0
    dw 0

test_001_do:
    mov si,#$0001
    mov ax,#test_001_source
    add ax,#8
    mov si,ax

    mov ax,#test_001_dest
    add ax,#8
    mov di,ax

    std
    mov cx,#3
    cmpsw
    jl test_001_ok1
    {get_tail_fail()}

test_001_ok1:
    mov bx,si
    mov ax,#test_001_source
    sub bx,ax
    cmp bx,#6
    jz test_001_ok2
    {get_tail_fail()}

test_001_ok2:
    mov bx,di
    mov ax,#test_001_dest
    sub bx,ax
    cmp bx,#6
    jz test_001_ok3
    {get_tail_fail()}

test_001_ok3:

test_002:
    mov si,#$0002
    jmp test_002_do

test_002_source:
    dw $1234
    dw $5678
    dw $9abc
    dw $def0

test_002_dest:
    dw 0
    dw 0
    dw 0
    dw 0

test_002_do:
    mov si,#$0002
    mov ax,#test_002_source
    mov si,ax

    mov ax,#test_002_dest
    mov di,ax

    cld
    mov cx,#4

    rep
    movsw

    cmp si,ax
    jz test_002_si_ok
    {get_tail_fail()}

test_002_si_ok:
    mov ax,#test_002_do
    cmp di,ax
    jz test_002_di_ok
    {get_tail_fail()}

test_002_di_ok:
    mov ax,[test_002_dest + 6]
    cmp [test_002_source + 6],ax
    jz test_002_xfer_ok
    {get_tail_fail()}

test_002_xfer_ok:
    jmp test_003_go

test_003:
    dw $7766
test_003_go:
    mov si,#$0003
    cld
    mov ax,#test_003
    mov si,ax
    lodsw
    cmp ax,#$7766
    jz test_003_ok1
    {get_tail_fail()}
test_003_ok1:
    mov ax,si
    cmp ax,#test_003_go
    jz test_003_ok2
    {get_tail_fail()}
test_003_ok2:

test_004:
    mov si,#$0004
    mov ax,#$9911
    not ax
    cmp ax,#$66ee
    jz test_004_ok
    {get_tail_fail()}
test_004_ok:
    jmp test_005_go

test_005:
    dw $1199
test_005_go:
    mov si,#$0005
    not word [test_005]
    mov ax,[test_005]
    cmp ax,#$ee66
    jz test_005_ok
    {get_tail_fail()}
test_005_ok:

test_006:
    mov si,#$0006
    ; make sure not to enable interrupts
    mov ax,#$fdff
    push ax
    popf
    lahf
    cmp ah,#$d7
    jz test_006_ok1
    {get_tail_fail()}
test_006_ok1:
    cmp al,#$ff
    jz test_006_ok2
    {get_tail_fail()}
test_006_ok2:
    mov ax,#$0000
    push ax
    popf
    lahf
    cmp ah,#$02
    jz test_006_ok3
    {get_tail_fail()}
test_006_ok3:
    cmp al,#$00
    jz test_006_ok4
    {get_tail_fail()}
test_006_ok4:

test_007:
    mov si,#$0007
    mov ax,#$fdff
    push ax
    popf
    mov al,#$00
    sahf
    pushf
    pop ax
    and ax,#$0fff
    cmp al,#$d7
    jz test_007_ok1
    {get_tail_fail()}
test_007_ok1:

test_008:
    mov si,#$0008
    ; clear flags
    xor ax,ax
    push ax
    popf
    ; enable interrupts
    sti
    pushf
    pop ax
    and ax,#$0fff
    and ax,#$200
    cmp ax,#512
    jz test_008_ok1
    {get_tail_fail()}
test_008_ok1:
    ; disable interrupts
    cli
    pushf
    pop bx
    and bx,#$200
    cmp bx,#0
    jz test_008_ok2
    {get_tail_fail()}
test_008_ok2:
    jmp test_009_go

test_009:
    dw $aaaa
test_009_go:
    mov si,#$0009
    xor ax,ax
    mov es,ax
    mov di,#test_009
    mov ax,#$bbbb
    std
    scasw
    jge test_009_ok1
    {get_tail_fail()}
test_009_ok1:
    add di,#2
    cmp di,#test_009
    jz test_009_ok2
    {get_tail_fail()}
test_009_ok2:

test_00a:
    dw $aa
test_00a_go:
    mov si,#$000a
    xor ax,ax
    mov es,ax
    mov di,#test_00a
    mov al,#$bb
    scasb
    jge test_00a_ok1
    {get_tail_fail()}
test_00a_ok1:
    inc di
    cmp di,#test_00a
    jz test_00a_ok2
    {get_tail_fail()}
test_00a_ok2:
    jmp test_00b_go

test_00b:
    db $a
    db $b
    db $c
    db $d
    db $e
    db $f
    db $1
    db $2
    db $3
test_00b_go:
    mov si,#$000b
    xor ax,ax
    mov ds,ax
    mov bx,#test_00b
    mov al,#$05
    xlatb
    cmp al,#$0f
    jz test_00b_ok1
    {get_tail_fail()}
test_00b_ok1:

test_00c:
    mov si,#$000c
    xor bx,bx
    xor dx,dx
    mov cx,#$256
test_00c_loop:
    inc bx
    inc dx
    cmp bx,#$123
    loopnz test_00c_loop
    cmp cx,#$133
    jz test_00c_ok1
    {get_tail_fail()}
test_00c_ok1:
    cmp dx,#$123
    jz test_00c_ok2
    {get_tail_fail()}
test_00c_ok2:

test_00d:
    mov si,#$000d
    xor bx,bx
    xor dx,dx
    mov cx,#$0009
test_00d_loop:
    inc bx
    inc dx
    cmp bx,dx
    loopz test_00d_loop
    cmp cx,#$0000
    jz test_00d_ok1
    {get_tail_fail()}
test_00d_ok1:
    cmp dx,#$09
    jz test_00d_ok2
    {get_tail_fail()}
test_00d_ok2:

test_00e:
    mov si,#$000e
    xor ax,ax
    jpe test_00e_ok1
    {get_tail_fail()}
test_00e_ok1:
    xor ax,#$1
    jpo test_00e_ok2
    {get_tail_fail()}
test_00e_ok2:
    xor ax,ax
    xor ax,#$3
    jpe test_00e_ok3
    {get_tail_fail()}
test_00e_ok3:

test_00f:
    mov si,#$000f
    mov bx,#3
    mov ax,#2
    sub bx,ax
    jns test_00f_ok1
    {get_tail_fail()}
test_00f_ok1:
    mov bx,#2
    mov ax,#3
    sub bx,ax
    js test_00f_ok2
    {get_tail_fail()}
test_00f_ok2:

test_010:
    mov si,#$0010
    mov bx,#$10
    cmp bx,#$08
    jnbe test_010_ok1
    {get_tail_fail()}
test_010_ok1:
    cmp bx,#$18
    jbe test_010_ok2
    {get_tail_fail()}
test_010_ok2:

; test of CMPSW & REPZ
test_011:
    mov si,#$0011
    jmp test_011_do

test_011_source:
    dw $0000
    dw $0000
    dw $dead
t011_source_after:
    dw $0000

test_011_dest:
    dw $0000
    dw $0000
    dw $beef
t011_dest_after:
    dw $0000

test_011_do:
    mov si,#$0011
    mov ax,#test_011_source
    mov si,ax

    mov ax,#test_011_dest
    mov di,ax

    cld
    mov cx,#4

    repz
    cmpsw

    cmp cx,#1
    jz test_011_cx_ok
    {get_tail_fail()}
test_011_cx_ok:

    mov ax,#t011_source_after
    cmp si,ax
    jz test_011_si_ok
    {get_tail_fail()}

test_011_si_ok:
    mov ax,#t011_dest_after
    cmp di,ax
    jz test_011_di_ok
    {get_tail_fail()}

test_011_di_ok:

finish:
''')

emit_tail(fh)

fh.close()
