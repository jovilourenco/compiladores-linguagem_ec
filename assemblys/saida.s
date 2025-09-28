  .section .text
.globl inc
inc:
    push %rbp
    mov %rsp, %rbp
    sub $8, %rsp

    mov $0, %rax
    mov %rax, -8(%rbp)
Linicio2:
    mov 16(%rbp), %rax
    push %rax
    mov -8(%rbp), %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setle %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfim3
    mov -8(%rbp), %rax
    push %rax
    mov $1, %rax
    pop %rbx
    add %rbx, %rax
    mov %rax, -8(%rbp)
    jmp Linicio2
Lfim3:
    mov -8(%rbp), %rax
    jmp Lret_inc_1

Lret_inc_1:
    add $8, %rsp
    pop %rbp
    ret


  .globl _start

_start:

    push %rbp
    mov %rsp, %rbp

    mov $7, %rax
    push %rax
    call inc
    add $8, %rsp
Lexit_main_0:


    call imprime_num
    call sair

    .include "runtime.s"

