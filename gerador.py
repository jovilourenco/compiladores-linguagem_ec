# João Victor Lourenço da Silva (20220005997)

from helpers.arvore import Const, OpBin, Var, Decl, Programa
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

# ===== Diretivas para variáveis (bss / comuns) =====
def vars_section(var_names: list[str]) -> str:
    """Cria diretivas .lcomm para reservar 8 bytes por variável (x86-64)."""
    if not var_names:
        return ""
    s = "  .section .bss\n"
    for v in var_names:
        s += f"  .lcomm {v}, 8\n"
    return s + "\n"


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
    """
    Recebe ast que deve ser um Programa (com declaracoes e resultado).
    Gera:
      - diretivas .lcomm para variáveis
      - código que avalia cada declaração e armazena o valor em memória
      - código que avalia a expressão final (deixando o resultado em %rax)
      - chamada ao runtime (imprime_num e sair)
    """
    # coletar nomes de variáveis (na ordem das declarações)
    var_names = []
    if isinstance(ast, Programa):
        var_names = [d.nome for d in ast.declaracoes]
    else:
        # compatibilidade: se receber apenas uma expressão, sem variáveis
        var_names = []

    asm = ""
    # diretivas de variáveis (antes do .text)
    asm += vars_section(var_names)
    # início da seção .text
    asm += header()

    # função recursiva que gera código e deixa resultado em %rax
    def rec(arv) -> str:
        if isinstance(arv, Const):
            return gen_const(arv.valor)
        if isinstance(arv, Var):
            # carregar variável da memória para %rax
            return f"    mov {arv.nome}, %rax\n"
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

    # 1) gerar código para cada declaração: calcular expressão e armazenar em variável
    if isinstance(ast, Programa):
        for d in ast.declaracoes:
            # avalia expressão da declaração (resultado em %rax)
            asm += rec(d.expr)
            # armazena %rax na variável d.nome
            asm += f"    mov %rax, {d.nome}\n"

        # 2) gerar código para expressão final (deixa resultado em %rax)
        asm += rec(ast.resultado)
    else:
        # compatibilidade: se ast for só uma expressão
        asm += rec(ast)

    # footer — imprime o número e sai
    asm += footer()
    return asm
