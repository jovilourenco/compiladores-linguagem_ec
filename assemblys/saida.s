  .section .text
.globl maioridade
maioridade:
    push %rbp
    mov %rsp, %rbp
    sub $8, %rsp

    mov $0, %rax
    mov %rax, -8(%rbp)
    mov $18, %rax
    push %rax
    mov 16(%rbp), %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setge %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfalso2
    mov $1, %rax
    mov %rax, -8(%rbp)
    jmp Lfim3
Lfalso2:
    mov $0, %rax
    mov %rax, -8(%rbp)
Lfim3:
    mov -8(%rbp), %rax
    jmp Lret_maioridade_1

Lret_maioridade_1:
    add $8, %rsp
    pop %rbp
    ret


  .globl _start

_start:

    push %rbp
    mov %rsp, %rbp

    mov $20, %rax
    push %rax
    call maioridade
    add $8, %rsp
Lexit_main_0:


    call imprime_num
    call sair

    .include "runtime.s"

