
  .section .text
  .globl _start

_start:
    mov $5, %rax
    push %rax
    mov $3, %rax
    push %rax
    mov $6, %rax
    pop %rbx
    div %rbx
    push %rax
    mov $15, %rax
    pop %rbx
    sub %rbx, %rax
    pop %rbx
    add %rbx, %rax

    call imprime_num
    call sair
    
    .include "runtime.s"
