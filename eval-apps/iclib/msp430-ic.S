.file "ic.S"

        .text
        .global suspend
        .global restore_registers

; @function void suspend_registers(uint16_t *registerSnapshot)
; @brief Captures register values into registerSnapshot before calling
;        c-routine for capturing volatile memory.
; Argument is in r12 by MSP430GCC standard
suspend:
        mov.w   sp, @r12
        add     #2, r12
        mov.w   sr, @r12
        add     #2, r12
        mov.w   r4, @r12
        add     #2, r12
        mov.w   r5, @r12
        add     #2, r12
        mov.w   r6, @r12
        add     #2, r12
        mov.w   r7, @r12
        add     #2, r12
        mov.w   r8, @r12
        add     #2, r12
        mov.w   r9, @r12
        add     #2, r12
        mov.w   r10, @r12
        add     #2, r12
        mov.w   r11, @r12
        add     #2, r12
        mov.w   r12, @r12
        add     #2, r12
        mov.w   r13, @r12
        add     #2, r12
        mov.w   r14, @r12
        add     #2, r12
        mov.w   r15, @r12

; Call c-routine to capture memory
        call    #suspendVM
        ret

; @function void restore_registers(uint16_t *registerSnapshot)
; @brief Restores register values and returns to saved return address
restore_registers:
        mov.w   @r12+, sp
        mov.w   @r12+, sr
        nop
        mov.w   @r12+, r4
        mov.w   @r12+, r5
        mov.w   @r12+, r6
        mov.w   @r12+, r7
        mov.w   @r12+, r8
        mov.w   @r12+, r9
        mov.w   @r12+, r10
        mov.w   @r12+, r11
        mov.w   @r12+, r12
        mov.w   @r12+, r13
        mov.w   @r12+, r14
        mov.w   @r12+, r15
        ret
