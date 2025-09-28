  .section .bss
  .lcomm i, 8
  .lcomm sum, 8

  .section .text

  .globl _start

_start:
    mov $0, %rax
    mov %rax, i(%rip)
    mov $0, %rax
    mov %rax, sum(%rip)

    push %rbp
    mov %rsp, %rbp

Linicio1:
    mov $5, %rax
    push %rax
    mov i(%rip), %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setle %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfim2
    mov sum(%rip), %rax
    push %rax
    mov i(%rip), %rax
    pop %rbx
    add %rbx, %rax
    mov %rax, sum(%rip)
    mov i(%rip), %rax
    push %rax
    mov $1, %rax
    pop %rbx
    add %rbx, %rax
    mov %rax, i(%rip)
    jmp Linicio1
Lfim2:
    mov sum(%rip), %rax
Lexit_main_0:


    call imprime_num
    call sair

    .include "runtime.s"

