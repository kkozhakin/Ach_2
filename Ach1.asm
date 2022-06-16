.include "m8def.inc"

.def sys = r16
.def letter_send = r17
.def T0_R = r18
.def T2_R = r19
.def LOOP_R = r20

.equ BAUD = 115200
.equ freq = 8000000
.equ UBRR_val = freq/(16*BAUD)-1
.equ TIMER1_INTERVAL = 235
.equ TIMER2_INTERVAL = 215

.cseg
.org 0x000
    rjmp MAIN
.org 0x004
    rjmp TIM2_OVF
.org 0x009
    rjmp TIM1_OVF

word1: .db "ping\r\n", 0 ,0
word2: .db "pong\r\n", 0 ,0

//Stack initialization
.macro  INITSTACK
    ldi sys, HIGH(RAMEND)
    out SPH, sys
    ldi sys, LOW(RAMEND)
    out SPL, sys
.endmacro

//Timers settings
TIMS_set:
    ldi sys, TIMER1_INTERVAL
    out TCNT0, sys
    ldi sys, TIMER2_INTERVAL
    out TCNT2, sys
    ldi sys, 0x2
    out TCCR0, sys
    ldi sys, 0x5
    out TCCR2, sys
    ldi sys, 0x101
    out TIMSK, sys
    ret

//USART settings
USART_set:
    ldi sys, high(UBRR_val)
    out UBRRH, sys
    ldi sys, low(UBRR_val)
    out UBRRL, sys
    ldi sys, 0x18
    out UCSRB, sys
    ldi sys, 0x86
    out UCSRC, sys
    ret

//Byte sending
TRANSMIT_BYTE:
    sbis UCSRA, UDRE
    rjmp TRANSMIT_BYTE 
    out UDR, letter_send
    ret

//First message sending
START_SEND_WORD1:
    ldi T0_R, TIMER2_INTERVAL
    out TCNT0, T0_R
    ldi ZH, high(2*word1)
    ldi ZL, low(2*word1)

NEW_BYTE_WORD1:
    lpm letter_send, Z+
    cpi letter_send, 0
    breq END_SEND_WORD1 
    rcall TRANSMIT_BYTE 
    rjmp NEW_BYTE_WORD1

END_SEND_WORD1:
    ret

//Second message sending
START_SEND_WORD2:
    ldi T2_R, TIMER2_INTERVAL
    out TCNT2, T2_R
    ldi ZH, high(2*word2)
    ldi ZL, low(2*word2)

NEW_BYTE_WORD2:
    lpm letter_send, Z+
    cpi letter_send, 0
    breq END_SEND_WORD2 
    rcall TRANSMIT_BYTE 
    rjmp NEW_BYTE_WORD2

END_SEND_WORD2:
    ret
    
//Main program
MAIN:
    INITSTACK
    rcall USART_set
    rcall TIMS_set
    sei
LOOP:
    rjmp LOOP

//Timer1 interruption
TIM1_OVF:
    sei
    rcall START_SEND_WORD1
    reti

//Timer2 interruption
TIM2_OVF:
    sei
    rcall START_SEND_WORD2
    reti