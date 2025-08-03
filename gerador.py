# João Victor Lourenço da Silva (20220005997)

from helpers.arvore import Const, OpBin
from helpers.token_tipos import Operadores

# ===== Modelos fixos assembly =====

def header():
    return f"""
  .section .text
  .globl _start

_start:
"""

def footer():
    return f"""
    call imprime_num
    call sair
    
    .include \"runtime.s\"
"""

# ===== Gerador =====

def gen_const(lit: int) -> str:
    # Geração de código de uma constante
    return f"    mov ${lit}, %rax\n"


def opBin_soma(opE_codigo: str, opD_codigo: str) -> str:
    # Gera código do operador ESQUERDO e dps DIREITO:
    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    pop %rbx\n" +
        "    add %rbx, %rax\n"
    )

def opBin_sub(opE_codigo: str, opD_codigo: str) -> str:
    # Gera código do operador DIREITO e dps ESQUERDO:
    return (
        opD_codigo +
        "    push %rax\n" +
        opE_codigo +
        "    pop %rbx\n" +
        "    sub %rbx, %rax\n"
    )

def opBin_mul(opE_codigo: str, opD_codigo: str) -> str:
    # Gera código do operador ESQUERDO e dps DIREITO:
    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    pop %rbx\n" +
        "    mul %rbx\n"
    )


def opBin_div(opE_codigo: str, opD_codigo: str) -> str:
    # Gera código do operador DIREITO e dps ESQUERDO:
    return (
        opD_codigo +
        "    push %rax\n" +
        opE_codigo +
        "    pop %rbx\n" +
        "    div %rbx\n"
    )

# ===== Função principal =====

def gera_codigo(ast) -> str:

    asm = header()

    def rec(arv) -> str: # Recursão que o professor montou.
        if isinstance(arv, Const):
            return gen_const(arv.valor)
        if isinstance(arv, OpBin):
            if arv.operador == Operadores.SOMA:
                left = rec(arv.opEsq)
                right = rec(arv.opDir)
                return opBin_soma(left, right)
            if arv.operador == Operadores.SUBTRACAO:
                left = rec(arv.opEsq)
                right = rec(arv.opDir)
                return opBin_sub(left, right)
            if arv.operador == Operadores.MULTIPLIC:
                left = rec(arv.opEsq)
                right = rec(arv.opDir)
                return opBin_mul(left, right)
            if arv.operador == Operadores.DIVISAO:
                left = rec(arv.opEsq)
                right = rec(arv.opDir)
                return opBin_div(left, right)
            else:
                raise NotImplementedError(f"Operação {arv.operador} não suportada ainda")
        raise NotImplementedError(f"Nó desconhecido: {arv}")

    asm += rec(ast)
    asm += footer()
    return asm
