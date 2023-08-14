#! /usr/bin/python3

from helpers import emit_header, emit_tail, get_tail_fail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'interrupt.asm', 'w')

emit_header(fh)

fh.write(f'''
	; skip over interrupt vector
	jmp skip_over_interrupt_vector

progress:
	dw $0

interrupt_triggered:
	db $00
send_eoi:
	db $01

	nop
	nop

kb_int_vector:
	push ax
	; retrieve character from keybboard
	in al,#$60
	; store
	mov interrupt_triggered,al
	;
	cmp send_eoi,#$01
	jnz skip_eoi
	;
	mov al,#$20  ; EOI code
	out $20,al  ; send 'end of interrupt'
	;
skip_eoi:
	pop ax
	iret

unmask_keyboard:
	; * PUT OCW1
	push AX
	; 8259 port 21
	mov al,#$fd
	; IMR, interrupt mask register
	; only allow irq 1
	out $21,al
	pop AX
	ret

mask_keyboard:
	; * PUT OCW1
	push AX
	; 8259 port 21
	mov al,#$ff
	; IMR, interrupt mask register
	; allow no interrupts
	out $21,al
	pop AX
	ret

clear_interrupt_flag:
	push ax
	xor ax,ax
	mov interrupt_triggered,al
	pop ax
	ret

wait_interrupt_success:
	push cx
	mov cx,#0000
loop_02:
	cmp byte interrupt_triggered,#$aa
	jz int_received
	loop loop_02
	hlt
int_received:
	pop cx
	ret

wait_interrupt_none:
	push cx
	mov cx,#0000
loop_win:
	cmp byte interrupt_triggered,#$aa
	jz win_int_received2
	loop loop_win
	jp loop_win_ok
win_int_received2:
	hlt ; error!
loop_win_ok:
	pop cx
	ret

reset_keyboard:
	; trigger keyboard reset
	; set kbd clk line low
	mov al,#$08
	out $61,al
	; this is 20ms on a 4.77MHz PC
	mov cx,#10582
loop_01:
	loop loop_01
	; set clk, enable lines high
	mov al,#$c8
	out $61,al
	; set clk high, enable low
	mov al,#$48
	out $61,al
	ret

; *** MAIN ***
skip_over_interrupt_vector:
	; set pointer to vector routine
	mov ax,#kb_int_vector
	mov [9 * 4 + 0],ax
	; set segment register to this code
	mov ax,cs
	mov [9 * 4 + 2],ax

	; * PUT ICW1
	; 8259 port 20
	mov al,#$0b
	; 00010011 -> ICW1, edge triggered, 8 byte int vector, single 8259, with ICW4
	out $20,al

	; * PUT ICW2?
	; 8259 port 21
	mov al,#$08
	; interrupt vector starting at 8
	out $21,al

	; NO ICW3 because the system has no slaves

	; * PUT ICW4
	; 00001101 -> sequential, buffered master, normal EOI, 80x86 mode
	mov al,#$0d
	out $21,al

	; ******** check if interrupts come when doing STI/CLI ********

	mov progress,#$0001

	call unmask_keyboard

	; just to be sure, redundant at this step
	call clear_interrupt_flag

	call reset_keyboard

	; enable interrupts
	sti

	; wait a while for an interrupt
	call wait_interrupt_success

	; disable interrupts
	cli

	call clear_interrupt_flag

	call reset_keyboard

	mov progress,#$0002

	; wait a while and make sure no interrupt comes in
	call wait_interrupt_none

	; * flush interrupt
	sti  ; enable interrupts
wait_for_int:
	cmp byte interrupt_triggered,#$aa
	jne wait_for_int
	; disable interrupts
	cli

	; ******** check if no interrupt comes in when doing STI and 8259 mask ********

	mov progress,#$100

	call mask_keyboard

	call clear_interrupt_flag

	sti

	call reset_keyboard

	; wait a while and make sure no interrupt comes in
	call wait_interrupt_none

	; ******** check if no interrupt comes in when the previous is not EOId ********

	mov progress,#$200

	call unmask_keyboard

	; make sure no EOI is send to the 8259
	mov send_eoi,#$00

	call clear_interrupt_flag

	; generate an interrupt
	call reset_keyboard
	; wait for the generated interrupt
	call wait_interrupt_success

	mov progress,#$201

	call clear_interrupt_flag
	; generate another interrupt
	call reset_keyboard
	call wait_interrupt_none

	; ***
''')

emit_tail(fh)

fh.close()
