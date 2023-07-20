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
    fh.write('\tmov ss,ax\n')  # set stack segment to 0
    fh.write('\tmov ax,#$800\n')  # set stack pointer
    fh.write('\tmov sp,ax\n')  # set stack pointer

