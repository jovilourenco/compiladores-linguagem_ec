
  .section .text
  .globl _start

_start:
    mov $2, %rax
    push %rax
    mov $4, %rax
    push %rax
    mov $10, %rax
    pop %rbx
    sub %rbx, %rax
    pop %rbx
    sub %rbx, %rax

    call imprime_num
    call sair
    
    .include "runtime.s"
