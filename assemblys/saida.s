  .section .bss
  .lcomm x, 8
  .lcomm y, 8


  .section .text
  .globl _start

_start:
    mov $7, %rax
    push %rax
    mov $4, %rax
    pop %rbx
    add %rbx, %rax
    push %rax
    mov $12, %rax
    pop %rbx
    mul %rbx
    mov %rax, x
    mov x, %rax
    push %rax
    mov $3, %rax
    pop %rbx
    mul %rbx
    push %rax
    mov $11, %rax
    pop %rbx
    add %rbx, %rax
    mov %rax, y
    mov x, %rax
    push %rax
    mov y, %rax
    pop %rbx
    mul %rbx
    push %rax
    mov x, %rax
    push %rax
    mov $11, %rax
    pop %rbx
    mul %rbx
    pop %rbx
    add %rbx, %rax
    push %rax
    mov y, %rax
    push %rax
    mov $13, %rax
    pop %rbx
    mul %rbx
    pop %rbx
    add %rbx, %rax

    call imprime_num
    call sair
    
    .include "runtime.s"
