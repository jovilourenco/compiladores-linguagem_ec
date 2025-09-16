# Teste

# Compiladores - Linguagem CMD

**Aluno:** João Victor Lourenço da Silva
**Matrícula:** 20220005997

Este projeto é a implementação em Python de um compilador para a linguagem **CMD**, desenvolvida como parte da atividade 09 da disciplina de Construção de Compiladores I.

---

## Sumário

- Gramática da Linguagem CMD
- Como Executar o Compilador
- Execução do Assembly Gerado
- Mensagens de Erro
- Testes Recomendados
- Exemplo de Assembly Gerado

---

## Gramática da Linguagem CMD

A gramática utilizada para a linguagem CMD é:

```python
programa ::= decl* '{' comando* 'return' exp ';' '}'
decl ::= IDENT '=' exp ';'
comando ::= atib | if | while
atrib ::= IDENT '=' exp ';'
if ::= 'if' exp '{' comando* '}' ( 'else' '{' comando* '}' )?
while ::= 'while' exp '{' comando* '}'
exp ::= exp_a ( ('<' | '>' | '==') exp_a )*
exp_a ::= exp_m (('+'|'-') exp_m)*
exp_m ::= prim (('*'|'/') prim)
prim ::= num | ident | '(' exp_c ')'
```

---

## Como Executar o Compilador

No diretório principal do projeto, execute o comando a seguir, substituindo o conteúdo de `_teste.txt` pelo programa que você deseja testar (em teste.txt existem alguns de exemplo):

Bash

`python main.py _teste.txt`

O `main.py` executa as seguintes etapas, nesta ordem:

1. **Análise Léxica**: Imprime os tokens encontrados.
2. **Análise Sintática**: Imprime a Árvore de Sintaxe Abstrata (AST).
3. **Geração e Avaliação**: Imprime a expressão gerada (`ast.gerador()`) e o resultado da avaliação/interpretação (`ast.avaliador()`).
4. **Visualização da AST**: Imprime a árvore de sintaxe abstrata em formato "rich".
5. **Geração de Assembly**: Cria o arquivo `saida.s` no diretório `assemblys`.

Também é possível executar cada módulo individualmente (por exemplo, `analisadorLexico.py` ou `analisadorSemantico.py`) para testes unitários.

---

## Execução do Assembly Gerado

O código assembly gerado utiliza a sintaxe AT&T (x86-64). 

No diretório `assemblys`, execute os seguintes comandos:

Bash

`as --64 -o saida.o saida.s
ld -o saida saida.o
./saida`

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
x = (7 + 4) * 12;
y = x * 3 + 11;
{
  return (x * y) + (x * 11) + (y * 13);
}
```

**Assembly Gerado (`assemblys/saida.s`):**

Snippet de código

```python
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

    ; ... código da expressão final ...

    call imprime_num
    call sair

    .include "runtime.s"
```