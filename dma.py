#! /usr/bin/python3

from helpers import emit_header
import sys

p = sys.argv[1]

fh = open(p + '/' + 'dma.asm', 'w')

emit_header(fh)


fh.write(
'''
test_001:
	MOV	AL, #0101B			; mask channel 1
	OUT	0AH, AL				; port 0AH set single channel mask
	XOR	AL, AL				; AX = 0000H (base address for DMA write)
	OUT	0CH, AL				; port 0CH clear F/L flip/flop
	OUT	02H, AL				; port 02H send low address byte (00H)
	OUT	02H, AL				; port 02H send high address byte (00H)
	MOV	AX, 1FFH			; set counter 200H bytes
	OUT	03H, AL				; port 03H send low counter byte (0FFH)
	MOV	AL, AH				; AL = high byte
	OUT	03H, AL				; port 03H send high counter byte (01FH)
	MOV	AL, 4				; set page register to seg 4000H
	OUT	83H, AL				; port 83H set page register ch 1
	MOV	AL, 10000101B		; set channel 1, Block Mode, Write
	OUT	0BH, AL				; port 0BH DMA mode reg
	MOV	AL, 0001B			; unmask channel 1
	OUT	0AH, AL				; port 0AH set single channel mask
	MOV	AL, 0101B			; set Request bit channel 1 (for mem-to-mem)
	OUT	09H, AL				; port 09H DMA start request

finish:
''')

fh.write('\tmov ax,#$a5ee\n')
fh.write('\tmov si,ax\n')  # set si to 'finished successfully'
fh.write('\thlt\n')
fh.close()
