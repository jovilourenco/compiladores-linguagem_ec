  .section .bss
  .lcomm x, 8

  .section .text
.globl foo
foo:
    push %rbp
    mov %rsp, %rbp
    sub $8, %rsp

    mov $5, %rax
    mov %rax, -8(%rbp)
    mov -8(%rbp), %rax
    jmp Lret_foo_1

Lret_foo_1:
    add $8, %rsp
    pop %rbp
    ret


  .globl _start

_start:
    # === inicializa variáveis globais ===
    mov $10, %rax
    mov %rax, x(%rip)

    # === main (bloco principal) ===
    push %rbp
    mov %rsp, %rbp

    call foo
Lexit_main_0:


    call imprime_num
    call sair

    .include "runtime.s"

