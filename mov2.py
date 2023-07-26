#! /usr/bin/python3

from configuration import *
from helpers import emit_header, emit_tail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'mov2.asm', 'w')

emit_header(fh)

fh.write(
f'''
    jmp skip_over_test_dws
test_dws:
    dw $1234
    dw $5678
test_dws_center:
    dw $9abc
    dw $def0
    dw $0000
    dw $0000
    dw $0000
    dw $0000
test_dw_direct:
    dw $beef

    dw $0000
    dw $0000

backup_dws:
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0

undo_changes:
    push ax
    push si
    push di
    push cx
    xor ax,ax
    mov ds,ax
    mov es,ax
    mov si,#backup_dws
    mov di,#test_dws
    mov cx,#11
    rep
    movsw
    pop cx
    pop di
    pop si
    pop ax
    ret

skip_over_test_dws:

; make a copy of the test-data
    mov si,#test_dws
    mov di,#backup_dws
    mov cx,#11
    rep
    movsw

''')

label = 'mov2_'

fh.write('; NEXT TEST GROUP\n')

# A0-A1
fh.write(f'''
; a0, MOV     al,rmb
    mov si,#test_dws
    mov al,[si + 2]
    cmp al,#$78
    jz {label}_a0_ok
    hlt
{label}_a0_ok:

; a1, MOV     al,rmw
    mov si,#test_dws
    mov ax,[si + 2]
    cmp ax,#$5678
    jz {label}_a1_ok
    hlt
{label}_a1_ok:
''')

# B0-BB

fh.write('; NEXT TEST GROUP\n')

for target in (
        ('b0', 'b4', 'b8', 'al', 'ah', 'ax'),
        ('b1', 'b5', 'b9', 'cl', 'ch', 'cx'),
        ('b2', 'b6', 'ba', 'dl', 'dh', 'dx'),
        ('b3', 'b7', 'bb', 'bl', 'bh', 'bx'),
        ):
    label = f'mov2_{target[3][0]}_'

    fh.write(f'''
; {target[0]}, MOV     {target[3]},ib
    mov {target[3]}, #$ff
    cmp {target[3]}, #$ff
    jz {label}_{target[0]}_ok
    hlt
{label}_{target[0]}_ok:

; {target[1]}, MOV     {target[4]},ib
    mov {target[4]}, #$9e
    cmp {target[4]}, #$9e
    jz {label}_{target[1]}_ok
    hlt
{label}_{target[1]}_ok:

; {target[2]}, MOV     {target[5]},ib
    mov {target[5]}, #$9e12
    cmp {target[5]}, #$9e12
    jz {label}_{target[2]}_ok
    hlt
{label}_{target[2]}_ok:

    ''')

# BC-BF

fh.write('; NEXT TEST GROUP\n')

for target in (
        ('sp', 'bc'),
        ('bp', 'bd'),
        ('si', 'be'),
        ('di', 'bf')
        ):
    fh.write(f'''
        ; MOV {target[0]},iw  {target[1]}
        mov ax,{target[0]}
        mov {target[0]},#$1234
        cmp {target[0]},#$1234
        jz {label}_{target[0]}_ok
        hlt
    {label}_{target[0]}_ok:
        mov {target[0]},ax

    ''')

fh.write(f'\tmov sp,{program_offset:04x}\n')

rmws = (
    ('[BX + SI]',  # R/M to work on/with
                '''
                MOV BX,#$4
                MOV SI,#test_dws
                ''',  # init for direction == 0 ([0] as a source)
                0xbc,  # test value *1
                '''
                MOV register,#$0d
                MOV BX,#$0
                MOV SI,#test_dws
                ''',  # init for direction == 1 ([0] as a destination)
                0x0d,  # test value
                True,  # skip if bl/bh/bx
                0x9abc  # word version of first test value (*1)
                ),
    ('[BX + DI]', '''
                MOV BX,#$4
                MOV DI,#test_dws + 1
                ''',
                0x9a,
                '''
                MOV register,#$0c
                MOV BX,#$0
                MOV DI,#test_dws + 1
                ''',
                0x0c,
                True,
                0xf09a
                ),
    ('[BX + SI + 2]', '''
                MOV BX,#$4
                MOV SI,#test_dws
                ''',
                0xf0,
                '''
                MOV register,#$0b
                MOV BX,#$4
                MOV SI,#test_dws
                ''',
                0x0b,
                True,
                0x00f0,
                ),
    ('[BX + DI + 2]', '''
                MOV BX,#$4
                MOV DI,#test_dws + 1
                ''',
                0xde,
                '''
                MOV register,#$0a
                MOV BX,#$4
                MOV DI,#test_dws + 1
                ''',
                0x0a,
                True,
                0xdef0
                ),

    ('[BP + SI]', '''
                MOV BP,#$4
                MOV SI,#test_dws
                ''',
                0xbc,
                '''
                MOV register,#$09
                MOV BP,#$4
                MOV SI,#test_dws
                ''',
                0x09,
                False,
                0x9abc
                ),
    ('[BP + DI]', '''
                MOV BP,#$4
                MOV DI,#test_dws + 1
                ''',
                0x9a,
                '''
                MOV register,#$08
                MOV BP,#$4
                MOV DI,#test_dws + 1
                ''',
                0x08,
                False,
                0xf09a
                ),
    ('[BP + SI + 2]', '''
                MOV BP,#$4
                MOV SI,#test_dws
                ''',
                0xf0,
                '''
                MOV register,#$07
                MOV BP,#$4
                MOV SI,#test_dws
                ''',
                0x07,
                False,
                0x00f0,
                ),
    ('[BP + DI + 2]', '''
                MOV BP,#$4
                MOV DI,#test_dws + 1
                ''',
                0xde,
                '''MOV register,#$06
                MOV BP,#$4
                MOV DI,#test_dws + 1
                ''',
                0x06,
                False,
                0xdef0,
                ),

    ('[SI]', '''
                MOV SI,#test_dws
                ''',
                0x34,
                '''
                MOV register,#$05
                MOV SI,#test_dws
                ''',
                0x05,
                False,
                0x5634
                ),
    ('[SI]', '''
                MOV SI,#test_dws + 1
                ''',
                0x12,
                '''
                MOV register,#$04
                MOV SI,#test_dws + 1
                ''',
                0x04,
                False,
                0x1234
                ),
    ('[DI]', '''
                MOV DI,#test_dws
                ''',
                0x34,
                '''
                MOV register,#$04
                MOV DI,#test_dws
                ''',
                0x04,
                False,
                0x5634
                ),
    ('[DI]', '''
                MOV DI,#test_dws + 1
                ''',
                0x12,
                '''
                MOV register,#$03
                MOV DI,#test_dws + 1
                ''',
                0x03,
                False,
                0x1234
                ),

    ('[SI + 2]', '''
                MOV SI,#test_dws
                ''',
                0x78,
                '''
                MOV register,#$02
                MOV SI,#test_dws
                ''',
                0x02,
                False,
                0x9a78
                ),
    ('[SI + 2]', '''
                MOV SI,#test_dws + 1
                ''',
                0x56,
                '''
                MOV register,#$01
                MOV SI,#test_dws + 1
                ''',
                0x01,
                False,
                0x5678
                ),
    ('[DI + 2]', '''
                MOV DI,#test_dws
                ''',
                0x78,
                '''
                MOV register,#$38
                MOV DI,#test_dws
                ''',
                0x38,
                False,
                0x9a78
                ),
    ('[DI + 2]', '''
                MOV DI,#test_dws + 1
                ''',
                0x56,
                '''
                MOV register,#$58
                MOV DI,#test_dws + 1
                ''',
                0x58,
                False,
                0x5678
                ),

    ('[BP]', '''
                MOV BP,#test_dws
                ''',
                0x34,
                '''
                MOV register,#$78
                MOV BP,#test_dws
                ''',
                0x78,
                False,
                0x3456
                ),
    ('[BP]', '''
                MOV BP,#test_dws + 1
                ''',
                0x12,
                '''
                MOV register,#$98
                MOV BP,#test_dws + 1
                ''',
                0x98,
                False,
                0x1234
                ),
    ('[BX]', '''
                MOV BX,#test_dws
                ''',
                0x34,
                '''
                MOV register,#$90
                MOV BX,#test_dws
                ''',
                0x90,
                True,
                0x3456
                ),
    ('[BX]', '''
                MOV BX,#test_dws + 1
                ''',
                0x12,
                '''
                MOV register,#$94
                MOV BX,#test_dws + 1
                ''',
                0x94,
                True,
                0x1234
                ),
    ('[BP + 2]', '''
                MOV BP,#test_dws
                ''',
                0x78,
                '''
                MOV register,#$14
                MOV BP,#test_dws
                ''',
                0x14,
                False,
                0x789a
                ),
    ('[BP + 2]', '''
                MOV BP,#test_dws + 1
                ''',
                0x56,
                '''
                MOV register,#$34
                MOV BP,#test_dws + 1
                ''',
                0x34,
                False,
                0x5678
                ),
    ('[BX + 2]', '''
                MOV BX,#test_dws
                ''',
                0x78,
                '''
                MOV register,#$32
                MOV BX,#test_dws
                ''',
                0x32,
                True,
                0x789a
                ),
    ('[BX + 2]', '''
                MOV BX,#test_dws + 1
                ''',
                0x56,
                '''
                MOV register,#$22
                MOV BX,#test_dws + 1
                ''',
                0x22,
                True,
                0x5678
                ),
    ('test_dw_direct', '''
                ''',
                0xef,
                '''
                MOV register,#$dd
                ''',
                0xdd,
                False,
                0xbeef
                ),
    )

# 8A  MOV     rb,rmb	mr d0 d1

fh.write('; NEXT TEST GROUP\n')

fh.write('\tcall undo_changes\n')
nr = 0
for direction in range(0, 2):
    sub_label = f'8a_{direction}_'

    for source in rmws:

        for target in (
                (0, 'al'),
                (1, 'cl'),
                (2, 'dl'),
                (3, 'bl'),
                (4, 'ah'),
                (5, 'dh'),
                (6, 'dh'),
                (7, 'bh'),
                ):

            if source[5] and (target[1] == 'bl' or target[1] == 'bh'):
                continue

            current_label = label + sub_label + f'{nr}'
            nr += 1

            if direction == 0:
                fh.write(f'''
                    {source[1]}

                    mov {target[1]},{source[0]}
                    cmp byte {target[1]},#${source[2]:02x}
                    jz {current_label}
                    hlt
                {current_label}:

                ''')

            elif direction == 1:
                fh.write(f'''
                    call undo_changes

                    {source[3].replace('register', target[1])}

                    mov {source[0]},{target[1]}
                    cmp byte {source[0]},#${source[4]:02x}
                    jz {current_label}
                    hlt
                {current_label}:

                ''')


            else:
                printf('Test generator internal error')
                sys.exit(1)

# A2-A3, C6-C7

fh.write('; NEXT TEST GROUP\n')

sub_label = f'a2a3_c6c7_'
nr = 0
for rmw in rmws:
    current_label = label + sub_label + f'{nr}'
    nr += 1

    # A2
    fh.write(f'''
        call undo_changes

        {rmw[1]}

        mov al,#$5f
        mov byte {rmw[0]},al
        cmp byte {rmw[0]},#$5f
        jz {current_label}_ok
        hlt
        {current_label}_ok:

    ''')

    # A3
    fh.write(f'''
        call undo_changes

        {rmw[1]}

        mov ax,#$5f92
        mov word {rmw[0]},ax
        cmp word {rmw[0]},#$5f92
        jz {current_label}_ok2
        hlt
        {current_label}_ok2:

    ''')

    # C6
    fh.write(f'''
        call undo_changes

        {rmw[1]}

        mov byte {rmw[0]},#$37
        cmp byte {rmw[0]},#$37
        jz {current_label}_ok3
        hlt
        {current_label}_ok3:

    ''')

    # C7
    fh.write(f'''
        call undo_changes

        {rmw[1]}

        mov word {rmw[0]},#$3278
        cmp word {rmw[0]},#$3278
        jz {current_label}_ok4
        hlt
        {current_label}_ok4:

    ''')

# 89/8B

fh.write('; NEXT TEST GROUP\n')

sub_label = f'898B_'
nr = 0
for rmw in rmws:
    for rw in ('ax', 'cx', 'dx', 'bx', 'sp', 'bp', 'si', 'di'):
        current_label = label + sub_label + f'{nr}'
        nr += 1

        # 89
        fh.write(f'''
            call undo_changes

            {rmw[1]}

            mov {rw},#$9911
            mov word {rmw[0]},{rw}
            cmp word {rmw[0]},#$9911
            jz {current_label}_ok
            hlt
            {current_label}_ok:
        ''')

        # 8B
        fh.write(f'''
            call undo_changes

            {rmw[1]}

            mov word {rmw[0]},#${rmw[6]:04x}
            mov word {rw},{rmw[0]}
            cmp word {rw},#${rmw[6]:04x}
            jz {current_label}_ok2
            hlt
            {current_label}_ok2:
        ''')

fh.write(f'\tmov sp,{program_offset:04x}\n')

# 8C/8E

fh.write('; NEXT TEST GROUP\n')

sub_label = f'8C8E_'
nr = 0
for rmw in rmws:
    for rw in ('ES', 'SS', 'DS'):  # skipping CS because problematic TODO
        current_label = label + sub_label + f'{nr}'
        nr += 1

        # 8C
        fh.write(f'''
            mov sp,{program_offset:04x}
            call undo_changes

            {rmw[1]}

            mov ax,#{nr + 1}
            mov {rw},ax
            db $2E ; 'CS prefix test1'
            mov {rmw[0]},{rw}

            db $2E
            mov bx,{rmw[0]}
            mov cx,{rw}

            cmp bx,cx
            jz {current_label}_ok
            hlt
            {current_label}_ok:

            xor ax,ax
            mov {rw},ax

        ''')

        # 8E
        fh.write(f'''
            mov sp,{program_offset:04x}
            call undo_changes

            {rmw[3].replace('register', 'ax')}

            mov {rw},{rmw[0]}
            mov dx,{rw}

            xor cx,cx
            mov {rw},cx

            mov ax,{rmw[0]}

            cmp ax,dx
            jz {current_label}_ok2
            hlt
            {current_label}_ok2:

            xor ax,ax
            mov {rw},ax

        ''')

emit_tail(fh)

fh.close()
