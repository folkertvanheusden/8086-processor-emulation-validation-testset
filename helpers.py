from configuration import *

def emit_header(fh):
    fh.write(f'\torg ${program_offset:04X}\n')
    fh.write('\n')

    fh.write('\tcli\n')  # disable interrupts
    fh.write('\n')
    fh.write('\tcld\n')  # string functions increment
    fh.write('\n')
    fh.write('\txor ax,ax\n')  # set si to 0
    fh.write('\tmov si,ax\n')
    fh.write('\n')
    fh.write('\tout $80,al\n')  # set "Manufacturing Diagnostics port" to 0
    fh.write('\n')
    fh.write('\tmov ss,ax\n')  # set stack segment to 0
    fh.write(f'\tmov ax,#${program_offset:04X}\n')  # set stack pointer
    fh.write('\tmov sp,ax\n')  # set stack pointer
    fh.write('\n')
    fh.write('\tmov ax,#intvec\n')  # make sure trace-int does not confuse anything
    fh.write('\tmov word [4],ax\n')
    fh.write('\txor ax,ax\n')
    fh.write('\tmov word [6],ax\n')
    fh.write('\tjmp init_continue\n')
    fh.write('intvec:\n')
    fh.write('\tiret\n')
    fh.write('init_continue:\n')

def emit_tail(fh):
    # to let emulator know all was fine
    fh.write('\tmov ax,#$a5ee\n')
    fh.write('\tmov si,ax\n')
    fh.write('\tmov al,#$ff\n')
    fh.write('\tout $80,al\n')  # set "Manufacturing Diagnostics port" to ff
    fh.write('\thlt\n')
