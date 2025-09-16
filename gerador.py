# João Victor Lourenço da Silva (20220005997)

from helpers.arvore import Const, OpBin, Var, Decl, Programa, Assign, IfStmt, WhileStmt, BlockStmt, ReturnStmt
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
    
    .include "runtime.s"
"""

# ===== Diretivas para variáveis (bss / comuns) =====
def vars_section(var_names: list[str]) -> str:
    # Se tiver variáveis, coloca a section e itera reservando espaços na memória
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
    # adiciona xor %rdx,%rdx antes do div para evitar lixo em RDX
    return (
        opD_codigo +
        "    push %rax\n" +
        opE_codigo +
        "    pop %rbx\n" +
        "    xor %rdx, %rdx\n" +
        "    div %rbx\n"
    )


# ===== Diretivas para geração de comandos =====
def cmp_equal(right_code: str, left_code: str) -> str:
    return (
        right_code +
        "    push %rax\n" +
        left_code +
        "    pop %rbx\n" +
        "    xor %rcx, %rcx\n" +
        "    cmp %rbx, %rax\n" +
        "    setz %cl\n" +
        "    mov %rcx, %rax\n"
    )

def cmp_less(right_code: str, left_code: str) -> str:
    return (
        right_code +
        "    push %rax\n" +
        left_code +
        "    pop %rbx\n" +
        "    xor %rcx, %rcx\n" +
        "    cmp %rbx, %rax\n" +
        "    setl %cl\n" +
        "    mov %rcx, %rax\n"
    )

def cmp_greater(right_code: str, left_code: str) -> str:
    return (
        right_code +
        "    push %rax\n" +
        left_code +
        "    pop %rbx\n" +
        "    xor %rcx, %rcx\n" +
        "    cmp %rbx, %rax\n" +
        "    setg %cl\n" +
        "    mov %rcx, %rax\n"
    )


# ===== Função principal =====

def gera_codigo(ast) -> str:
    """
    Recebe um Programa (com declaracoes e resultado).
    e Gera:
      - variáveis
      - código que avalia cada declaração e armazena o valor em memória
      - código que avalia a expressão final (deixando o resultado em %rax)
      - chamada o runtime (imprime_num e sair)
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

    # contador de rótulos para gerar nomes únicos
    label_counter = {"n": 0}
    def new_label(base: str) -> str:
        i = label_counter["n"]
        label_counter["n"] += 1
        return f"{base}{i}"

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
            # Comparadores: gerar RIGHT primeiro (conforme enunciado), depois LEFT
            if arv.operador == Operadores.IGUAL_IGUAL:
                right = rec(arv.opDir)
                left = rec(arv.opEsq)
                return cmp_equal(right, left)
            if arv.operador == Operadores.MENOR:
                right = rec(arv.opDir)
                left = rec(arv.opEsq)
                return cmp_less(right, left)
            if arv.operador == Operadores.MAIOR:
                right = rec(arv.opDir)
                left = rec(arv.opEsq)
                return cmp_greater(right, left)
            
            else:
                raise NotImplementedError(f"Operação {arv.operador} não suportada ainda")
        raise NotImplementedError(f"Nó desconhecido: {arv}")

    # rótulo de saída para returns
    exit_label = new_label("Lexit")

    # gera código para um statement (atribuição, if, while, bloco, return)
    def gen_stmt(stmt) -> str:

        if isinstance(stmt, ReturnStmt):
            code = rec(stmt.expr)   # deixa valor em %rax
            code += f"    jmp {exit_label}\n"
            return code

        if isinstance(stmt, Assign):
            # Avalia RHS e armazena em memória
            code = rec(stmt.expr)
            code += f"    mov %rax, {stmt.nome}\n"
            return code

        if isinstance(stmt, IfStmt):
            # gerar rótulos
            l_false = new_label("Lfalso")
            l_end = new_label("Lfim")
            code = ""
            # condição -> %rax
            code += rec(stmt.cond)
            # testar %rax == 0
            code += "    cmp $0, %rax\n"
            code += f"    jz {l_false}\n"
            # then branch
            for s in stmt.then_stmts:
                code += gen_stmt(s)
            # pular else
            code += f"    jmp {l_end}\n\n"
            # else label
            code += f"{l_false}:\n"
            if stmt.else_stmts is not None:
                for s in stmt.else_stmts:
                    code += gen_stmt(s)
            code += f"\n{l_end}:\n"
            return code

        if isinstance(stmt, WhileStmt):
            l_begin = new_label("Linicio")
            l_end = new_label("Lfim")
            code = ""
            code += f"{l_begin}:\n"
            # condição
            code += rec(stmt.cond)
            code += "    cmp $0, %rax\n"
            code += f"    jz {l_end}\n"
            # corpo
            for s in stmt.body:
                code += gen_stmt(s)
            # voltar ao início
            code += f"    jmp {l_begin}\n\n"
            code += f"{l_end}:\n"
            return code

        if isinstance(stmt, BlockStmt):
            code = ""
            for s in stmt.stmts:
                code += gen_stmt(s)
            return code

        raise NotImplementedError(f"Stmt desconhecido: {stmt}")


    # 1) gerar código para cada declaração: calcular expressão e armazenar em variável
    if isinstance(ast, Programa):
        for d in ast.declaracoes:
            # avalia expressão da declaração (resultado em %rax)
            asm += rec(d.expr)
            # armazena %rax na variável d.nome
            asm += f"    mov %rax, {d.nome}\n"
        # 2) gerar código para os comandos do corpo (em ordem)
        for c in ast.comandos:
            asm += gen_stmt(c)
        # 3) gerar código para expressão final (deixa resultado em %rax)
        asm += rec(ast.resultado)
    else:
        # compatibilidade: se ast for só uma expressão
        asm += rec(ast)

    # insere label de saída usado por returns dentro dos blocos
    asm += f"{exit_label}:\n"

    # footer — imprime o número e sai
    asm += footer()
    return asm
