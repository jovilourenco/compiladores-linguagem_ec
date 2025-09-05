# compiladores-linguagem\_ev

**Aluno:** João Victor Lourenço da Silva
**Matrícula:** 20220005997

Implementação em Python de um compilador para a linguagem **EV** (extensão de EC) — linguagem de expressões com declarações de variáveis — conforme atividade 08 da disciplina de Construção de Compiladores I.

---

## Sumário

* Gramática da linguagem EV
* Códigos refatorados com relação a EC
* Como executar
* Execução do assembly
* Mensagens de erro (o que esperar)
* Testes recomendados
* Exemplo de assembly gerado
* Observações do compilador

---

## Gramática da linguagem EV

A gramática utilizada para EV foi:

```
decl  ::= IDENT '=' exp ';'
programa ::= decl* '=' exp EOF

exp_a ::= exp_m (( '+' | '-' ) exp_m)*
exp_m ::= prim (( '*' | '/' ) prim)*
prim   ::= num | ident | '(' exp_a ')'
```

* `IDENT` — identificador: letra seguida de letras/dígitos (`[A-Za-z][A-Za-z0-9]*`).
* `num` — sequência de dígitos (`[0-9]+`).
* `=` inicia a expressão final (resultado).
* `;` termina cada declaração.
* Precedência/associatividade: `*`/`/` têm precedência sobre `+`/`-`; todas left-associative.

---

## Refatorações com relação a EC

1. **Tokenização / Analisador Léxico**

   * Tokens: `NUMERO`, `IDENT`, operadores (`+ - * /`), pontuação (`( ) = ;`) e `EOF`.
   * Regra especial: se uma sequência começar por dígito e depois contiver letras (`237axy`) → token `LEX_ERROR`.
   * Cada `Token` guarda `tipo`, `lexema`, `pos` e `linha`.

2. **Analisador Sintático**

   * Entrada: `parse_programa()` que implementa `decl* '=' exp EOF`.
   * Cada `decl` é `IDENT '=' exp ';'` (ponto-e-vírgula obrigatório — modo estrito).
   * `prim` aceita `num`, `ident` e parênteses.
   * Em erros sintáticos é lançada a exceção `ParserError` com `linha` e `pos`.

3. **Árvore (AST)**

   * Nós: `Const`, `Var`, `OpBin`, `Decl`, `Programa`.
   * `Programa.avaliador()` avalia declarações em ordem, mantendo `env` (tabela de símbolos); `Var.avaliador(env)` lança `NameError` se variável não estiver declarada.

4. **Gerador**

   * Reserva espaço para variáveis com `.lcomm <nome>, 8`.
   * Para cada `Decl`, gera código da expressão (resultado em `%rax`) e armazena em memória: `mov %rax, nome(%rip)`.
   * `Var` gera `mov nome(%rip), %rax`.
   * Mantém estratégia do professor (push/pop para operações binárias) e chama `imprime_num` e `sair` no final.

5. **Helpers**

   * Impressão de AST com `rich` (`helpers/arvore_print_rich.py`), adaptada para `Programa`, `Decl`, `Var`, `OpBin`, `Const`.
   * `main.py` contém todo o fluxo: léxico → sintático → impressão → avaliação → geração. (Seria o compilador de fato)

---

## Como executar

No diretório principal do projeto executar:

```bash
python main.py _teste.txt
```

O `main.py` realiza, nesta ordem:

1. Análise léxica (imprime tokens)
2. Análise sintática (imprime AST)
3. Impressão da expressão gerada (`ast.gerador()`)
4. Avaliação/interpretador (`ast.avaliador()`) — mostra resultado final
5. Impressão da estrutura da árvore de sintaxe abstrata com `rich`
6. Geração de assembly em `assemblys/saida.s`

Podemos executar as etapas isoladamente, só rodar o módulo ao invés do main.py (por exemplo, o analisadorLexicoEV.py ou o analisadorSintaticoEV.py). Usei muito para testes de unidade :D.

---

## Execução do assembly

No diretório `assemblys`, com ajuda do WSL, visto que tenho Windows, executo:

```bash
cd assemblys
as --64 -o saida.o saida.s
ld -o saida saida.o
./saida
```

* Sintaxe: AT\&T (x86-64).
* O `runtime.s` deve prover `imprime_num` e `sair` (incluso pelo `footer()` do gerador).

---

## Mensagens de erro (o que esperar)

### Erros léxicos

* **Token inválido** (caractere não reconhecido): token `Error.LEX_ERROR` com lexema do fragmento (`@`, `#`, etc.).
* **Número seguido de letras** (ex.: `237axy`): token `LEX_ERROR` com lexema completo.

### Erros sintáticos

* Falta de `;` numa declaração → `ParserError` com `linha` e `pos` indicando onde esperava `;`.
* Falta de `=` iniciando expressão final → `ParserError` com indicação do local.
* Parênteses não balanceados ou token inesperado → `ParserError` com linha/pos.

### Erros semânticos / de execução

* Uso de variável não declarada → `NameError` com mensagem:
  `Erro semântico: variável '<nome>' não declarada (linha <l>, pos <p>)`.
* Divisão por zero → `ZeroDivisionError: Divisão por zero`.

---

## Testes recomendados

Coloquei alguns testes e o que eles retornam no arquivo `testes.txt`. Para testá-los, basta pegar o exemplo e colocar em `_teste.txt`. O main.py sempre utilizará ele para rodar.

---

## Exemplo de assembly gerado para o programa:
x = (7 + 4) * 12;
y = x * 3 + 11;
= (x * y) + (x * 11) + (y * 13)

```asm
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
    mov %rax, x(%rip)

    mov x(%rip), %rax
    push %rax
    mov $3, %rax
    pop %rbx
    mul %rbx
    push %rax
    mov $11, %rax
    pop %rbx
    add %rbx, %rax
    mov %rax, y(%rip)

    ; ... código da expressão final ...

    call imprime_num
    call sair

    .include "runtime.s"
```

---

## Observações do compilador

* **Ponto-e-vírgula obrigatório**: o parser exige `;` após cada declaração (comportamento estrito).
* **Fase de análise semântica separada**: hoje a verificação de variáveis e erros semânticos ocorre durante a avaliação (`Programa.avaliador()`).

Diz o que prefere em seguida.
