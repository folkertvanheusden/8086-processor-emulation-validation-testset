def emit_header(fh):
    fh.write('\torg $800\n')
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
    fh.write('\tmov ax,#$800\n')  # set stack pointer
    fh.write('\tmov sp,ax\n')  # set stack pointer


def emit_tail(fh):
    # to let emulator know all was fine
    fh.write('\tmov ax,#$a5ee\n')
    fh.write('\tmov si,ax\n')
    fh.write('\tmov al,#$ff\n')
    fh.write('\tout $80,al\n')  # set "Manufacturing Diagnostics port" to ff
    fh.write('\thlt\n')
