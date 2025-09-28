# Teste

# Compiladores - Linguagem Fun

**Aluno:** João Victor Lourenço da Silva
**Matrícula:** 20220005997

Este projeto é a implementação em Python de um compilador para a linguagem **FUN**, desenvolvida como parte da atividade 10 da disciplina de Construção de Compiladores I.

---

## Sumário

- Gramática da Linguagem CMD
- Como Executar o Compilador
- Execução do Assembly Gerado
- Mensagens de Erro
- Testes Recomendados
- Exemplo de Assembly Gerado

---

## Gramática da Linguagem FUN

A gramática utilizada para a linguagem FUN é:

```python
programa ::= decl* 'main' '{' comando* 'return' exp ';' '}'
decl ::= vardecl | fundecl
vardecl ::= 'var' IDENT '=' exp ';'
fundecl ::= 'fun' IDENT '(' arglist? ')' '{' vardecl* comando* 'return' exp ';' '}'
arglist ::= IDENT (',' IDENT)*
comando ::= atrib | if | while | bloco
atrib ::= IDENT '=' exp ';'
if ::= 'if' '(' exp ')' '{' comando* '}' ( 'else' '{' comando* '}' )?
while ::= 'while' '(' exp ')' '{' comando* '}'
bloco ::= '{' comando* '}'
exp ::= exp_a ( ('<' | '>' | '==') exp_a )*
exp_a ::= exp_m (('+'|'-') exp_m)*
exp_m ::= prim ((''|'/') prim)
prim ::= NUM | IDENT | IDENT '(' explist? ')' | '(' exp ')'
explist ::= exp (',' exp)*
```

Algo que observo: Na implementação dessa gramática, criei uma pequena variação. Após um comando como `if` ou `while`, o programa espera um '('. o formato dos comandos é algo do tipo: `comando (expressão) '{'comando'}'`

Apenas essa alteração.

---

## Como Executar o Compilador

No diretório principal do projeto, primeiro, instale o rich `pip install rich` e, depois execute o comando a seguir, substituindo o conteúdo de `_teste.txt` pelo programa que você deseja testar (em teste.txt existem alguns de exemplo):

Bash

`python main.py _teste.txt`

O `main.py` executa as seguintes etapas, nesta ordem:

1. **Análise Léxica**: Imprime os tokens encontrados.
2. **Análise Sintática**: Imprime a Árvore de Sintaxe Abstrata (AST).
3. **Checagem semântica**: tabela de símbolos, offsets.
4. **Avaliação e interpretação**: Imprime a expressão gerada (`ast.gerador()`) e o resultado da avaliação/interpretação (`ast.avaliador()`).
5. **Visualização da AST**: Imprime a árvore de sintaxe abstrata em formato "rich".
6. **Geração de Assembly**: Cria o arquivo `saida.s` no diretório `assemblys`.

Também é possível executar cada módulo individualmente (por exemplo, `analisadorLexico.py`, `analisadorSemantico.py` ou `analisadorSemantico.py`) para testes unitários.

Observo que, agora, para manter o padrão de modularização, criei o analisador semântico para manter e gerenciar a tabela de símbolos e offsets do código de máquina.

---

## Execução do Assembly Gerado

O código assembly gerado utiliza a sintaxe AT&T (x86-64). 

No diretório `assemblys`, execute os seguintes comandos:

Bash

```cd assemblys
as --64 -o saida.o saida.s
ld -o saida saida.o
./saida
```

**Observação**: O arquivo `runtime.s` é incluído automaticamente pelo gerador do compilador e fornece as funções `imprime_num` e `sair`, necessárias para a execução do programa.

---

## Mensagens de Erro

Aqui estão alguns tipos de erro que você pode encontrar:

### Erros Léxicos

- **Token inválido**: Caractere não reconhecido, resultando em um erro do tipo `LEX_ERROR`.
- **Número seguido de letras**: Exemplo: `237axy`, também gera um erro `LEX_ERROR`.

### Erros Sintáticos

- **Falta de `;`**: Em declarações ou atribuições.
- **Blocos incompletos**: Ausência de `{` ou `}` em blocos de código.
- **`return` fora de lugar**: O comando `return` só pode ser usado no final do programa principal.
- **Tokens inesperados**: Gera um `ParserError` com a linha e posição do erro.

### Erros Semânticos / De Execução

- **Variável não declarada**: O uso de uma variável que não foi previamente declarada causa um `NameError`.
- **Atribuição para variável não declarada**.
- **Divisão por zero**: Gera um `ZeroDivisionError`.

---

## Testes Recomendados

O arquivo `testes.txt` contém uma variedade de exemplos de código, tanto válidos quanto com erros. Para testar o compilador, basta copiar o exemplo desejado para o arquivo `_teste.txt` e executar o `main.py`.

---

## Exemplo de Assembly Gerado

A seguir, um exemplo de código CMD e o respectivo assembly gerado.

**Código CMD:**

```python
fun fact(n) {
  var r = 0;
  if (n < 2) {
    r = 1;
  } else {
    r = n * fact(n - 1);
  }
  return r;
}

main {
  return fact(6);
}
```

**Assembly Gerado (`assemblys/saida.s`):**

Snippet de código

```python
  .section .text
.globl fact
fact:
    push %rbp
    mov %rsp, %rbp
    sub $8, %rsp

    mov $0, %rax
    mov %rax, -8(%rbp)
    mov $2, %rax
    push %rax
    mov 16(%rbp), %rax
    pop %rbx
    xor %rcx, %rcx
    cmp %rbx, %rax
    setl %cl
    mov %rcx, %rax
    cmp $0, %rax
    jz Lfalso2
    mov $1, %rax
    mov %rax, -8(%rbp)
    jmp Lfim3
Lfalso2:
    mov 16(%rbp), %rax
    push %rax
    mov 16(%rbp), %rax
    push %rax
    mov $1, %rax
    pop %rbx
    sub %rax, %rbx
    mov %rbx, %rax
    push %rax
    call fact
    add $8, %rsp
    pop %rbx
    mul %rbx
    mov %rax, -8(%rbp)
Lfim3:
    mov -8(%rbp), %rax
    jmp Lret_fact_1

Lret_fact_1:
    add $8, %rsp
    pop %rbp
    ret


  .globl _start

_start:

    push %rbp
    mov %rsp, %rbp

    mov $6, %rax
    push %rax
    call fact
    add $8, %rsp
Lexit_main_0:


    call imprime_num
    call sair

    .include "runtime.s"
```
