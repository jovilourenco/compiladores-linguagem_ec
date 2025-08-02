  #
  # modelo de saida para o compilador
  #

  .section .text
  .globl _start

_start:
  ## saida do compilador deve ser inserida aqui

  mov $7271, %rax
  mov $617, %rbx
  mul %rbx
  mov %rax, %rcx
  mov $11222, %rax
  mov $256, %rbx
  mul %rbx
  add %rcx, %rax
  mov %rax, %rcx
  mov $17179869426, %rax
  add %rcx, %rax

  call imprime_num
  call sair

  .include "runtime.s"
  
