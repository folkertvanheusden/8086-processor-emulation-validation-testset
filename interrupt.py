#! /usr/bin/python3

from helpers import emit_header, emit_tail, get_tail_fail
import sys

p = sys.argv[1]

fh = open(p + '/' + 'interrupt.asm', 'w')

emit_header(fh)

fh.write(f'''
	; skip over interrupt vector
	jmp skip_over_interrupt_vector

interrupt_triggered:
	db $00
kb_int_vector:
	push ax
	; retrieve character from keybboard
	in al,#$60
	; store
	mov interrupt_triggered,al
	;
	mov al,#$20  ; EOI code
	out $20,al  ; send 'end of interrupt'
	;
	pop ax
	iret

clear_interrupt_flag:
	push ax
	xor ax,ax
	mov interrupt_triggered,al
	pop ax
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
	mov al,#$00
	; interrupt vector 0
	out $21,al

	; NO ICW3 because the system has no slaves

	; * PUT ICW4
	; 00001101 -> sequential, buffered master, normal EOI, 80x86 mode
	mov al,#$0d
	out $21,al

	; ******** check if interrupts come when doing STI/CLI ********

	; * PUT OCW1
	; 8259 port 21
	mov al,#$fd
	; IMR, interrupt mask register
	; only allow irq 1
	out $21,al

	; just to be sure, redundant at this step
	call clear_interrupt_flag

	call reset_keyboard

	; enable interrupts
	sti

	; wait a while for an interrupt
	mov cx,#0000
loop_02:
	cmp byte interrupt_triggered,#$aa
	jz int_received
	loop loop_02
	hlt

int_received:
	; disable interrupts
	cli

	call clear_interrupt_flag

	call reset_keyboard

	; wait a while and make sure no interrupt comes in
	mov cx,#0000
loop_03:
	cmp byte interrupt_triggered,#$aa
	jz int_received2
	loop loop_03
	jp loop_03_ok
int_received2:
	hlt ; error!
loop_03_ok:

	; * flush interrupt
	sti  ; enable interrupts
wait_for_int:
	cmp byte interrupt_triggered,#$aa
	jne wait_for_int
	; disable interrupts
	cli

	; ******** check if no interrupt comes in when doing STI and 8259 mask ********

	; * PUT OCW1
	; 8259 port 21
	mov al,#$ff
	; IMR, interrupt mask register
	; allow no interrupts
	out $21,al

	call clear_interrupt_flag

	sti

	call reset_keyboard

	; wait a while and make sure no interrupt comes in
	mov cx,#0000
loop_04:
	cmp byte interrupt_triggered,#$0
	jnz int_received3
	loop loop_04
	jp loop_04_ok
int_received3:
	hlt
loop_04_ok:
''')

emit_tail(fh)

fh.close()
