  .section .bss
  .lcomm a, 8
  .lcomm b, 8


  .section .text
  .globl _start

_start:
    mov $5, %rax
    mov %rax, a
    mov $5, %rax
    mov %rax, b
    mov b, %rax
    push %rax
    mov a, %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setl %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfalso1
    mov $1, %rax
    jmp Lexit0
    jmp Lfim2

Lfalso1:
    mov b, %rax
    push %rax
    mov a, %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setz %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfalso3
    mov $2, %rax
    jmp Lexit0
    jmp Lfim4

Lfalso3:
    mov $3, %rax
    jmp Lexit0

Lfim4:

Lfim2:
    mov $0, %rax
Lexit0:

    call imprime_num
    call sair
    
    .include "runtime.s"
