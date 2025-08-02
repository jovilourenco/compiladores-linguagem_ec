
from arvore import Const, OpBin
from token_tipos import Operadores

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
    """
    Gera instrução para carregar constante em %rax.
    """
    return f"    mov ${lit}, %rax\n"


def opBin_soma(opE_codigo: str, opD_codigo: str) -> str:
    # Gera código do operador esquerdo e do direito:

    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    pop %rbx\n" +
        "    add %rbx, %rax\n"
    )

# ===== Função principal =====

def gera_codigo(ast) -> str:
    # Recursão que o professor montou.

    asm = header()

    def rec(arv) -> str:
        # retorna o trecho de assembly que deixa o valor de arv em %rax
        if isinstance(arv, Const):
            return gen_const(arv.valor)
        if isinstance(arv, OpBin):
            if arv.operador == Operadores.SOMA:
                left = rec(arv.opEsq)
                right = rec(arv.opDir)
                return opBin_soma(left, right)
            else:
                raise NotImplementedError(f"Operação {arv.operador} não suportada ainda")
        raise NotImplementedError(f"Nó desconhecido: {arv}")

    asm += rec(ast)
    asm += footer()
    return asm
