#! /usr/bin/python3

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

backup_dws:
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0
    dw 0

undo_changes:
    mov si,#backup_dws
    mov di,#test_dws
    mov cx,#8
    rep
    movsw
    ret

skip_over_test_dws:

; make a copy of the test-data
    mov si,#test_dws
    mov di,#backup_dws
    mov cx,#8
    rep
    movsw

''')

label = 'mov2_'

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

# 8A  MOV     rb,rmb	mr d0 d1
fh.write('\tcall undo_changes\n')
for direction in range(0, 2):
    sub_label = f'8a_{direction}_'
    nr = 0

    for source in (
            ('[BX + SI]', '''
                        MOV BX,#$4
                        MOV SI,#test_dws
                        ''',
                        0xbc,
                        '''
                        MOV register,#$0d
                        MOV BX,#$0
                        MOV SI,#test_dws
                        ''',
                        0x0d
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
                        0x0c
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
                        0x0b
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
                        0x0a
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
                        0x09
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
                        0x08
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
                        0x07
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
                        0x06
                        ),

            ('[SI]', '''
                        MOV SI,#test_dws
                        ''',
                        0x34,
                        '''
                        MOV register,#$05
                        MOV SI,#test_dws
                        ''',
                        0x05
                        ),
            ('[SI]', '''
                        MOV SI,#test_dws + 1
                        ''',
                        0x12,
                        '''
                        MOV register,#$04
                        MOV SI,#test_dws + 1
                        ''',
                        0x04
                        ),
            ('[DI]', '''
                        MOV DI,#test_dws
                        ''',
                        0x34,
                        '''
                        MOV register,#$04
                        MOV DI,#test_dws
                        ''',
                        0x04
                        ),
            ('[DI]', '''
                        MOV DI,#test_dws + 1
                        ''',
                        0x12,
                        '''
                        MOV register,#$03
                        MOV DI,#test_dws + 1
                        ''',
                        0x03
                        ),

            ('[SI + 2]', '''
                        MOV SI,#test_dws
                        ''',
                        0x78,
                        '''
                        MOV register,#$02
                        MOV SI,#test_dws
                        ''',
                        0x02
                        ),
            ('[SI + 2]', '''
                        MOV SI,#test_dws + 1
                        ''',
                        0x56,
                        '''
                        MOV register,#$01
                        MOV SI,#test_dws + 1
                        ''',
                        0x01
                        ),
            ('[DI + 2]', '''
                        MOV DI,#test_dws
                        ''',
                        0x78,
                        '''
                        MOV register,#$38
                        MOV DI,#test_dws
                        ''',
                        0x38
                        ),
            ('[DI + 2]', '''
                        MOV DI,#test_dws + 1
                        ''',
                        0x56,
                        '''
                        MOV register,#$58
                        MOV DI,#test_dws + 1
                        ''',
                        0x58
                        ),

            ('[BP]', '''
                        MOV BP,#test_dws
                        ''',
                        0x34,
                        '''
                        MOV register,#$78
                        MOV BP,#test_dws
                        ''',
                        0x78
                        ),
            ('[BP]', '''
                        MOV BP,#test_dws + 1
                        ''',
                        0x12,
                        '''
                        MOV register,#$98
                        MOV BP,#test_dws + 1
                        ''',
                        0x98
                        ),
            ('[BX]', '''
                        MOV BX,#test_dws
                        ''',
                        0x34,
                        '''
                        MOV register,#$90
                        MOV BX,#test_dws
                        ''',
                        0x90
                        ),
            ('[BX]', '''
                        MOV BX,#test_dws + 1
                        ''',
                        0x12,
                        '''
                        MOV register,#$94
                        MOV BX,#test_dws + 1
                        ''',
                        0x94
                        ),
            ('[BP + 2]', '''
                        MOV BP,#test_dws
                        ''',
                        0x78,
                        '''
                        MOV register,#$14
                        MOV BP,#test_dws
                        ''',
                        0x14
                        ),
            ('[BP + 2]', '''
                        MOV BP,#test_dws + 1
                        ''',
                        0x56,
                        '''
                        MOV register,#$34
                        MOV BP,#test_dws + 1
                        ''',
                        0x34
                        ),
            ('[BX + 2]', '''
                        MOV BX,#test_dws
                        ''',
                        0x78,
                        '''
                        MOV register,#$32
                        MOV BX,#test_dws
                        ''',
                        0x32
                        ),
            ('[BX + 2]', '''
                        MOV BX,#test_dws + 1
                        ''',
                        0x56,
                        '''
                        MOV register,#$22
                        MOV BX,#test_dws + 1
                        ''',
                        0x22
                        ),
            ):

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
            current_label = label + sub_label + f'{nr}'
            nr += 1

            if direction == 0:
                fh.write(f'''
                    {source[1]}

                    mov {target[1]},{source[0]}
                    cmp {target[1]},#${source[2]:02x}
                    jz {current_label}
                    hlt
                {current_label}:

                ''')

            elif direction == 1:
                fh.write(f'''
                    call undo_changes

                    {source[3].replace('register', target[1])}

                    mov {source[0]},{target[1]}
                    cmp {source[0]},#${source[4]:02x}
                    jz {current_label}
                    hlt
                {current_label}:

                ''')


            else:
                printf('Test generator internal error')
                sys.exit(1)

emit_tail(fh)

fh.close()
