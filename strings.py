#! /usr/bin/python3

from flags import parity, flags_inc_dec16
from helpers import emit_header, emit_tail, emit_tail_fail, get_tail_fail
from values_16b import b16_values
import sys

p = sys.argv[1]

fh = None
n_tests = 0

nr = 0

def header():
    global fh

    if fh == None:
        file_name = f'strings_{n_tests}.asm'
        fh = open(p + '/' + file_name, 'w')

        emit_header(fh)

        fh.write('\tjmp near go\n')

        fh.write('from_start:\n')
        fh.write('\t.space 1024\n')
        fh.write('from_end:\n')

        fh.write('to_start:\n')
        fh.write('\t.space 1024\n')
        fh.write('to_end:\n')

        fh.write('fill_buffers:\n')
        fh.write('\tcld\n')
        fh.write('\tmov di,#from_start\n')
        fh.write('\tmov cx,#(from_end - from_start)\n')
        fh.write('\trep\n')
        fh.write('\tstosb\n')
        fh.write('\ttest cx,#$0\n')
        fh.write('\tjnz fill_buffers_fail\n')
        fh.write('\tstd\n')
        fh.write('\tmov di,#to_end\n')
        fh.write('\tdec di\n')
        fh.write('\tmov cx,#(to_end - to_start)\n')
        fh.write('\tmov al,#$a5\n')
        fh.write('\trep\n')
        fh.write('\tstosb\n')
        fh.write('\ttest cx,#$0\n')
        fh.write('\tjnz fill_buffers_fail\n')
        fh.write('\tret\n')

        fh.write('fill_buffers_fail:\n')
        emit_tail_fail(fh)

        fh.write('go:\n')
        fh.write('\tcld\n')

# JCXZ and (no-)others
def emit_test(cx, taken):
    global fh
    global n_tests

    for instr in range(0, 1):
        header()

        # test itself
        label = f'test_{instr}_{cx:04x}'

        fh.write(f'{label}:\n')

        # reset flags
        fh.write(f'\txor ax,ax\n')
        fh.write(f'\tpush ax\n')
        fh.write(f'\tpopf\n')

        fh.write(f'\tmov cx,#${cx:04x}\n')

        if instr == 0:  # JCXZ
            check_flags = None

            fh.write(f'\tJCXZ {label}_taken\n')

            if taken:
                emit_tail_fail(fh)
                fh.write(f'{label}_taken:\n')

            else:
                fh.write(f'\tjmp {label}_continue\n')
                fh.write(f'{label}_taken:\n')
                emit_tail_fail(fh)
                fh.write(f'{label}_continue:\n')

        # keep flags
        if not check_flags is None:
            fh.write(f'\tpushf\n')

        # verify flags
        if not check_flags is None:
            fh.write(f'ok_{label}:\n')
            fh.write(f'\tpop ax\n')
            fh.write(f'\tand ax,#$0fff\n')
            fh.write(f'\tcmp ax,#${check_flags:04x}\n')
            fh.write(f'\tjz next_{label}\n')
            emit_tail_fail(fh)

        fh.write(f'next_{label}:\n')
        fh.write('\n')

        n_tests += 1

        if (n_tests % 512) == 0:
            emit_tail(fh)

            fh.close()
            fh = None

for val in ((0, True), (1, False), (128, False), (32768, False), (65535, False)):
    emit_test(val[0], val[1])

header()

# STOSB
label = 'stosb'
fh.write('\tmov al,#$ee\n')
fh.write(f'\tcall fill_buffers\n')

fh.write('\tmov di,#from_start\n')
fh.write('\tmov cx,#(from_end - from_start)\n')
fh.write(f'{label}_loop:\n')
fh.write('\tmovb al,[di]\n')
fh.write('\tcmp al,#$ee\n')
fh.write(f'\tjne {label}_fail\n')
fh.write(f'\tloop {label}_loop\n')
fh.write(f'\tjmp {label}_oksofar\n')
fh.write(f'{label}_fail:\n')
emit_tail_fail(fh)
fh.write(f'{label}_oksofar:\n')
fh.write('\ttest cx,#$0\n')
fh.write(f'\tjz {label}_ok_end\n')
emit_tail_fail(fh)
fh.write(f'{label}_ok_end:\n')

fh.write('\tmov di,#to_start\n')
fh.write('\tmov cx,#(to_end - to_start)\n')
fh.write(f'to{label}_loop:\n')
fh.write('\tmovb al,[di]\n')
fh.write('\tcmp al,#$a5\n')
fh.write(f'\tjne to{label}_fail\n')
fh.write(f'\tloop to{label}_loop\n')
fh.write(f'\tjmp to{label}_oksofar\n')
fh.write(f'to{label}_fail:\n')
emit_tail_fail(fh)
fh.write(f'to{label}_oksofar:\n')
fh.write('\ttest cx,#$0\n')
fh.write(f'\tjz to{label}_ok_end\n')
emit_tail_fail(fh)
fh.write(f'to{label}_ok_end:\n')

# MOVSB
label = 'movsb'
fh.write('\tmov al,#$99\n')
fh.write(f'\tcall fill_buffers\n')
fh.write('\tmov si,#from_start\n')
fh.write('\tmov di,#to_start\n')
fh.write('\tmov cx,#(from_end - from_start)\n')
fh.write('\trep\n')
fh.write('\tmovsb\n')
fh.write('\tmov di,#to_start\n')
fh.write('\tmov cx,#(to_end - to_start)\n')
fh.write(f'{label}_loop2:\n')
fh.write('\tmovb al,[di]\n')
fh.write('\tcmp al,#$99\n')
fh.write(f'\tjne {label}_fail2\n')
fh.write(f'\tloop {label}_loop2\n')
fh.write(f'\tjmp {label}_oksofar2\n')
fh.write(f'{label}_fail2:\n')
emit_tail_fail(fh)
fh.write(f'{label}_oksofar2:\n')
fh.write('\ttest cx,#$0\n')
fh.write(f'\tjz {label}_ok_end2\n')
emit_tail_fail(fh)
fh.write(f'{label}_ok_end2:\n')

# MOVSB reverse order
label = 'movsb'
fh.write('\tmov al,#$67\n')
fh.write(f'\tcall fill_buffers\n')

fh.write('\tmov ax,#from_end\n')
fh.write('\tsub ax,#1\n')
fh.write('\tmov si,ax\n')

fh.write('\tmov ax,#to_end\n')
fh.write('\tdec ax\n')
fh.write('\tmov di,ax\n')

fh.write('\tmov cx,#(from_end - from_start)\n')

fh.write(f'\tstd\n')

fh.write('\trep\n')
fh.write('\tmovsb\n')

fh.write(f'\tcld\n')

fh.write('\tmov di,#to_end\n')
fh.write('\tdec di\n')
fh.write('\tmov cx,#(to_end - to_start)\n')

fh.write(f'{label}_loop2b:\n')
fh.write('\tmovb al,[di]\n')
fh.write('\tcmp al,#$67\n')
fh.write(f'\tjne {label}_fail2b\n')
fh.write(f'\tloop {label}_loop2b\n')
fh.write(f'\tjmp {label}_oksofar2b\n')
fh.write(f'{label}_fail2b:\n')
emit_tail_fail(fh)
fh.write(f'{label}_oksofar2b:\n')
fh.write('\ttest cx,#$0\n')
fh.write(f'\tjz {label}_ok_end2b\n')
emit_tail_fail(fh)
fh.write(f'{label}_ok_end2b:\n')

# LODSB (or any other) starting with CX==0
fh.write(f'''
    mov cx,#$0000
    mov ax,#$1000
    mov si,ax
    mov di,ax
    rep
    lodsb
    cmp cx,#$0000
    jz cx0_rep_ok1
    {get_tail_fail()}
cx0_rep_ok1:
    mov bx,si
    cmp bx,#$1000
    jz cx0_rep_ok2
    {get_tail_fail()}
cx0_rep_ok2:
    mov bx,di
    cmp bx,#$1000
    jz cx0_rep_ok3
    {get_tail_fail()}
cx0_rep_ok3:
''')

emit_tail(fh)

fh.close()
