/*
 * Copyright (c) 2018-2020, University of Southampton.
 * All rights reserved.
 *
 * SPDX-License-Identifier: BSD-3-Clause
 */

.file "ic.S"
.cpu cortex-m0
.text
.thumb

/* @function void suspend_stack_and_regs(uint32_t *saved_sp, int * snapshotValid, uint8_t *stackSnapshot)
 * @brief pushes registers to stack, and saves stack pointer to savedSp, then
 *        sleeps.
 */
.globl suspend_stack_and_regs
.type suspend_stack_and_regs, %function
suspend_stack_and_regs:
    // Push core registers to stack
    push {r0-r7,lr}
    mov r3, r8
    mov r4, r9
    mov r5, r10
    mov r6, r11
    mov r7, r12
    push {r3-r7}
    mrs r4, apsr /*# should this be xpsr?*/
    push {r4}

    // Save stack pointer in NVM @r0
    mov r7, sp
    str r7, [r0]

    // Save stack to NVM
    ldr r4, =__boot_stack_high // Use different stack
    mov sp, r4
    push {r0-r3} // Safekeep function arguments
    mov r1, r7     // src: stack (saved)
    ldr r4, =__stack_high
    sub r4, r4, r7 // len: r4 = stack_high - sp
    ldr r5, =__stack_size
    add r0, r2, r5 // dst: r5 = snapshotValid + (stack_size-len)
    sub r0, r0, r4
    mov r2, r4
    bl memcpy
    pop {r0-r3}

    // Set flag & suspend execution
    mov r4, #1
    str r4, [r1] //Set snapshotValid
    mov r4, #0
    ldr r5, =0x40000030 // OUTPORT_OUT
    str r4, [r5] //de-assert keepAlive
    wfe
suspend_loop0: // Should never get here
    nop
    b suspend_loop0

/*
 * @function void suspend_and_flush_cache(uint32_t *saved_sp, int *snapshotValid)
 * @brief Pushes registers to stack and flushes data cache
 */
.globl suspend_and_flush_cache
.type suspend_and_flush_cache, %function
suspend_and_flush_cache:
    // Push core registers to stack
    push {r0-r7,lr}
    mov r3, r8
    mov r4, r9
    mov r5, r10
    mov r6, r11
    mov r7, r12
    push {r3-r7}
    mrs r4, apsr /*# should this be xpsr?*/
    push {r4}

    // Save stack pointer in NVM @r0
    mov r7, sp
    str r7, [r0]

    // Flush cache
    mov r4, #0x2 // DCACHE_CTRL_FLUSH
    ldr r5, =0x40000010 // DCACHE_CTRL_CSR
    str r4, [r5]
  safc_loop0: // while(flushing)
    ldr r4, [r5]
    cmp r4, #0x2
    beq safc_loop0

    // Set flag & suspend execution
    mov r4, #1
    str r4, [r1] //Set snapshotValid
    mov r4, #0
    ldr r5, =0x40000030 // OUTPORT_OUT
    str r4, [r5] //de-assert keepAlive
    wfe
  safc_loop1:
    nop
    b safc_loop1

/*
 * @function void restore_registers(uint16_t *saved_sp)
 * @brief Restores register values and returns to saved return address
 */
.globl restore_registers
.type restore_registers, %function
restore_registers:
    /* get stack pointer and recover registers */
    ldr r1, [r0, #0]
    mov sp, r1
    pop {r1}
    msr apsr_nzcvq, r1
    pop {r3-r7}
    mov r8, r3
    mov r9, r4
    mov r10, r5
    mov r11, r6
    mov r12, r7
    pop {r0-r7, pc}
