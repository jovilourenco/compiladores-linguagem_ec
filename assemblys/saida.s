  .section .text
.globl a
a:
    push %rbp
    mov %rsp, %rbp

    mov 16(%rbp), %rax
    push %rax
    call b
    add $8, %rsp
    push %rax
    mov $1, %rax
    pop %rbx
    add %rbx, %rax
    jmp Lret_a_1

Lret_a_1:
    pop %rbp
    ret

.globl b
b:
    push %rbp
    mov %rsp, %rbp

    mov 16(%rbp), %rax
    push %rax
    mov $2, %rax
    pop %rbx
    mul %rbx
    jmp Lret_b_2

Lret_b_2:
    pop %rbp
    ret


  .globl _start

_start:

    push %rbp
    mov %rsp, %rbp

    mov $3, %rax
    push %rax
    call a
    add $8, %rsp
Lexit_main_0:


    call imprime_num
    call sair

    .include "runtime.s"

