
  .section .text
  .globl _start

_start:
    mov $30, %rax
    push %rax
    mov $2, %rax
    push %rax
    mov $2, %rax
    pop %rbx
    add %rbx, %rax
    pop %rbx
    add %rbx, %rax

    call imprime_num
    call sair
    
    .include "runtime.s"
