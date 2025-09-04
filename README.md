# compiladores-linguagem\_ev

**Aluno:** João Victor Lourenço da Silva
**Matrícula:** 20220005997

Implementação em Python de um compilador para a linguagem **EV** (extensão de EC) — linguagem de expressões com declarações de variáveis — conforme atividade 08 da disciplina de Construção de Compiladores I.

---

## Sumário

* Gramática da linguagem EV
* Etapas implementadas
* Estrutura de arquivos
* Como executar
* Geração de assembly (montagem e execução)
* Mensagens de erro (o que esperar)
* Testes recomendados (conteúdo e resultado esperado)
* Exemplo de assembly gerado (trecho)
* Observações, limitações e extensões possíveis
* Nomes de arquivo / placeholders

---

## Gramática da linguagem EV

A gramática utilizada (conforme enunciado da atividade) é:

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

## Etapas implementadas

1. **Tokenização / Lexer**

   * Tokens: `NUMERO`, `IDENT`, operadores (`+ - * /`), pontuação (`( ) = ;`) e `EOF`.
   * Regra especial: se uma sequência começar por dígito e depois contiver letras (`237axy`) → token `LEX_ERROR`.
   * Cada `Token` guarda `tipo`, `lexema`, `pos` e `linha`.

2. **Parser (analisador sintático)**

   * Entrada: `parse_programa()` que implementa `decl* '=' exp EOF`.
   * Cada `decl` é `IDENT '=' exp ';'` (ponto-e-vírgula obrigatório — modo estrito).
   * `prim` aceita `num`, `ident` e parênteses.
   * Em erros sintáticos é lançada a exceção `ParserError` com `linha` e `pos`.

3. **Árvore (AST)**

   * Nós: `Const`, `Var`, `OpBin`, `Decl`, `Programa`.
   * `Programa.avaliador()` avalia declarações em ordem, mantendo `env` (tabela de símbolos); `Var.avaliador(env)` lança `NameError` se variável não estiver declarada.

4. **Gerador de código (assembly x86-64 AT\&T)**

   * Reserva espaço para variáveis com `.lcomm <nome>, 8`.
   * Para cada `Decl`, gera código da expressão (resultado em `%rax`) e armazena em memória: `mov %rax, nome(%rip)`.
   * `Var` gera `mov nome(%rip), %rax`.
   * Mantém estratégia do professor (push/pop para operações binárias) e chama `imprime_num` e `sair` no final.

5. **Ferramentas auxiliares**

   * Impressão de AST com `rich` (`helpers/arvore_print_rich.py`), adaptada para `Programa`, `Decl`, `Var`, `OpBin`, `Const`.
   * `main.py` integra o fluxo: léxico → sintático → impressão → avaliação → geração.

---

## Estrutura de arquivos (sugestão)

```
.
├─ main.py                        # script que executa todas as etapas
├─ analisadorLexicoEV.py          # lexer (substitua se o nome for diferente)
├─ analisadorSintaticoEV.py       # parser (substitua se o nome for diferente)
├─ gerador.py                     # gerador de assembly
├─ runtime.s                      # runtime (imprime_num, sair)
├─ assemblys/                     # saída do gerador (saida.s)
└─ helpers/
   ├─ token_tipos.py
   ├─ token.py
   ├─ arvore.py                   # classes AST (Const, Var, OpBin, Decl, Programa)
   ├─ arvore_print_rich.py
   └─ ... (outros helpers)
```

> Se algum nome for diferente no seu repositório, substitua nos comandos abaixo.

---

## Como executar

No diretório principal do projeto execute:

```bash
python main.py <programa.txt>
```

Exemplo:

```bash
python main.py test_valid_program.txt
```

O `main.py` realiza, nesta ordem:

1. Análise léxica (imprime tokens)
2. Análise sintática (imprime AST)
3. Impressão da expressão gerada (`ast.gerador()`)
4. Avaliação/interpretador (`ast.avaliador()`) — mostra resultado final
5. Impressão da árvore com `rich`
6. Geração de assembly em `assemblys/saida.s`

Se preferir executar somente etapas isoladas, rode os módulos correspondentes (por exemplo, o lexer ou o parser) conforme seus nomes de arquivo.

---

## Geração de assembly — montagem e execução

No diretório `assemblys` execute:

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

## Testes recomendados (arquivos .txt)

Coloque cada bloco em um arquivo separado e rode `python main.py <arquivo>` para verificar o comportamento.

1. `test_valid_program.txt` (válido)

```
x = (7 + 4) * 12;
y = x * 3 + 11;
= (x * y) + (x * 11) + (y * 13)
```

* Esperado: passa todas as fases; resultado `60467`; `assemblys/saida.s` gerado.

2. `test_lex_error_numstart.txt` (erro léxico)

```
x = 237axy + 1;
= x
```

* Esperado: lexer produz `LEX_ERROR` com lexema `237axy`.

3. `test_missing_semicolon.txt` (erro sintático)

```
x = 7 + 4
= x
```

* Esperado: `ParserError` por falta de `;`.

4. `test_missing_final_equal.txt` (erro sintático)

```
x = 1;
# sem linha iniciando por '=' para expression final
```

* Esperado: `ParserError` — falta `=` iniciando expressão final.

5. `test_undeclared_variable.txt` (erro semântico)

```
x = 7 + y;
= x
```

* Esperado: `NameError` informando `y` não declarada (linha/pos).

6. `test_unbalanced_parentheses.txt` (erro sintático)

```
x = (7 + 4;
= x
```

* Esperado: `ParserError` ao esperar `)`.

7. `test_division_by_zero.txt` (erro de execução)

```
x = 7;
y = x - 7;
= x / y
```

* Esperado: `ZeroDivisionError`.

8. `test_invalid_char_token.txt` (erro léxico)

```
x = 7 @ 3;
= x
```

* Esperado: `LEX_ERROR` para `@`.

---

## Exemplo de assembly gerado (trecho) — `test_valid_program.txt`

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

## Observações, limitações e extensões possíveis

* **Ponto-e-vírgula obrigatório**: o parser exige `;` após cada declaração (comportamento estrito). Posso alterar para aceitar `EOF` como terminador final se preferir comportamento REPL-friendly.
* **Fase de análise semântica separada**: hoje a verificação de variáveis e erros semânticos ocorre durante a avaliação (`Programa.avaliador()`). Posso adicionar uma função `verifica_semantica(programa)` que percorre a AST e relata todos os erros sem executar.
* **Formato de armazenamento de variáveis**: uso `.lcomm` para reservar espaço; se quiser `.data` com inicializadores, posso adaptar.
* **Mensagens de erro com trecho do código**: posso estender `ParserError` para mostrar a linha fonte com um caret apontando para a posição do token.

---

## Nomes de arquivo / placeholders

Substitua os nomes abaixo caso seus arquivos tenham nomes diferentes:

* Lexer: `analisadorLexicoEV.py` → `_____`
* Parser: `analisadorSintaticoEV.py` → `_____`
* Gerador: `gerador.py` → `_____`
* Runtime: `runtime.s` → `_____`
* Saída assembly: `assemblys/saida.s` → `_____`

---

Se quiser, eu posso:

* gravar este arquivo `.md` no repositório (já criado aqui como documento),
* gerar automaticamente os arquivos de teste (`test_*.txt`) para você, ou
* implementar a fase `verifica_semantica(programa)` separada.

Diz o que prefere em seguida.
