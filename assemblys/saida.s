  .section .bss
  .lcomm a, 8
  .lcomm b, 8
  .lcomm r, 8


  .section .text
  .globl _start

_start:
    mov $18, %rax
    mov %rax, a
    mov $12, %rax
    mov %rax, b
    mov $0, %rax
    mov %rax, r
    mov a, %rax
    mov %rax, r
Linicio1:
    mov b, %rax
    push %rax
    mov r, %rax
    push %rax
    mov $1, %rax
    pop %rbx
    add %rbx, %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setg %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfim2
    mov b, %rax
    push %rax
    mov r, %rax
    pop %rbx
    sub %rbx, %rax
    mov %rax, r
    jmp Linicio1

Lfim2:
Linicio3:
    mov $0, %rax
    push %rax
    mov r, %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setg %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfim4
    mov b, %rax
    mov %rax, a
    mov r, %rax
    mov %rax, b
    mov a, %rax
    mov %rax, r
Linicio5:
    mov b, %rax
    push %rax
    mov r, %rax
    push %rax
    mov $1, %rax
    pop %rbx
    add %rbx, %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setg %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfim6
    mov b, %rax
    push %rax
    mov r, %rax
    pop %rbx
    sub %rbx, %rax
    mov %rax, r
    jmp Linicio5

Lfim6:
    jmp Linicio3

Lfim4:
    mov b, %rax
Lexit0:

    call imprime_num
    call sair
    
    .include "runtime.s"
