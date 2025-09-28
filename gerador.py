# João Victor Lourenço da Silva (20220005997)

from helpers.arvore import (
    Const, OpBin, Var, Decl, Programa,
    Assign, IfStmt, WhileStmt, BlockStmt, ReturnStmt, FunDecl, Call
)
from helpers.token_tipos import Operadores

# ===== Modelos fixos assembly =====

def header():
    return f"""
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


# ===== Gerador helpers (expressões básicas) =====

def gen_const(lit: int) -> str:
    # Geração de código de uma constante (deixa valor em %rax)
    return f"    mov ${lit}, %rax\n"

def opBin_soma(opE_codigo: str, opD_codigo: str) -> str:
    # avaliar esquerda, push; avaliar direita; pop left em %rbx; rax = right + left
    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    pop %rbx\n" +
        "    add %rbx, %rax\n"
    )

def opBin_sub(opE_codigo: str, opD_codigo: str) -> str:
    # padrão: avaliar esquerda, push; avaliar direita; pop left em %rbx; calcular left - right
    # queremos resultado em %rax
    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    pop %rbx\n" +
        "    sub %rax, %rbx\n" +    # rbx = left - right
        "    mov %rbx, %rax\n"
    )

def opBin_mul(opE_codigo: str, opD_codigo: str) -> str:
    # padrão: avaliar esquerda, push; avaliar direita; pop left em %rbx; rax = right * left (usando imul)
    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    pop %rbx\n" +
        "    mul %rbx\n"    # rax = rax * rbx
    )

def opBin_div(opE_codigo: str, opD_codigo: str) -> str:
    # divisão inteira com sinal: avaliar esquerda, push; avaliar direita; mover divisor pra %rbx;
    # pop left em %rax; preparar RDX:RAX e idiv %rbx
    return (
        opE_codigo +
        "    push %rax\n" +
        opD_codigo +
        "    mov %rax, %rbx\n" +   # rbX = divisor (right)
        "    pop %rax\n" +        # rax = dividend (left)
        "    xor %rdx, %rdx\n" +
        "    div %rbx\n"
    )

def opBin_mod(opE_codigo: str, opD_codigo: str) -> str:
    # left % right  --> calcula resto (usa idiv, resto em %rdx)
    return (
        opE_codigo +                
        "    push %rax\n" +
        opD_codigo +                # deixa right (divisor) em %rax
        "    mov %rax, %rbx\n" +    
        "    pop %rax\n" +          
        "    xor %rdx, %rdx\n" +    
        "    div %rbx\n" +          # depois da divisão, o resto sempre fica em %rdx
        "    mov %rdx, %rax\n"      # resultado = resto -> %rax
    )

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

def cmp_le(right_code: str, left_code: str) -> str:
    return (
        right_code +
        "    push %rax\n" +
        left_code +
        "    pop %rbx\n" +
        "    xor %rcx, %rcx\n" +
        "    cmp %rbx, %rax\n" +
        "    setle %cl\n" +
        "    mov %rcx, %rax\n"
    )

def cmp_ge(right_code: str, left_code: str) -> str:
    return (
        right_code +
        "    push %rax\n" +
        left_code +
        "    pop %rbx\n" +
        "    xor %rcx, %rcx\n" +
        "    cmp %rbx, %rax\n" +
        "    setge %cl\n" +
        "    mov %rcx, %rax\n"
    )

def cmp_ne(right_code: str, left_code: str) -> str:
    return (
        right_code +
        "    push %rax\n" +
        left_code +
        "    pop %rbx\n" +
        "    xor %rcx, %rcx\n" +
        "    cmp %rbx, %rax\n" +
        "    setne %cl\n" +
        "    mov %rcx, %rax\n"
    )


# ===== Gerador principal =====

def gera_codigo(ast) -> str:
    """
    Recebe um Programa (var_decls, fun_decls, comandos (main), resultado).
    Gera:
      - seção .bss com variáveis globais
      - código em .text:
         - inicializa variáveis globais
         - executa comandos do main (com support para return)
         - gera definições de funções (labels), cada função com prologue/epilogue
      - chamada ao runtime (imprime_num e sair)
    Observações:
      - funções devem ter campos param_offsets, local_offsets e frame_size (calculados pelo analisador semântico)
      - acesso a variáveis locais/params usa offsets relativos a %rbp
      - acesso a variáveis globais usa RIP-relative: name(%rip)
    """
    asm = ""

    # coletar nomes de variáveis globais
    var_names = []
    if isinstance(ast, Programa):
        var_names = [d.nome for d in ast.var_decls]
    else:
        var_names = []

    # diretivas bss
    asm += vars_section(var_names)
    asm += "  .section .text\n"  # Adicionado para iniciar .text antes das funções

    # contador de rótulos
    label_counter = {"n": 0}
    def new_label(base: str) -> str:
        i = label_counter["n"]
        label_counter["n"] += 1
        return f"{base}{i}"

    # helper para formatar offset(%rbp)
    def rbp_addr(offset: int) -> str:
        # offset já contém sinal quando negativo (por exemplo -8)
        # no assembly precisa ser como -8(%rbp) ou 16(%rbp)
        return f"{offset}(%rbp)"

    # função recursiva que gera código para expressões e deixa resultado em %rax
    def rec(expr, current_fun: FunDecl | None) -> str:
        if isinstance(expr, Const):
            return gen_const(expr.valor)

        if isinstance(expr, Var):
            name = expr.nome
            # se estamos dentro de uma função e a variável é local/param -> usar offset
            if current_fun is not None:
                local_offs = getattr(current_fun, 'local_offsets', {})
                param_offs = getattr(current_fun, 'param_offsets', {})
                if name in local_offs:
                    off = local_offs[name]
                    return f"    mov {rbp_addr(off)}, %rax\n"
                if name in param_offs:
                    off = param_offs[name]
                    return f"    mov {rbp_addr(off)}, %rax\n"
            # caso global:
            return f"    mov {name}(%rip), %rax\n"

        if isinstance(expr, Call):
            # Avaliar argumentos e empilhar em ordem inversa (último primeiro)
            code = ""
            for a in reversed(expr.args):
                code += rec(a, current_fun)
                code += "    push %rax\n"
            code += f"    call {expr.nome}\n"
            nargs = len(expr.args)
            if nargs > 0:
                code += f"    add ${8 * nargs}, %rsp\n"
            return code

        if isinstance(expr, OpBin):
            if expr.operador == Operadores.SOMA:
                left = rec(expr.opEsq, current_fun)
                right = rec(expr.opDir, current_fun)
                return opBin_soma(left, right)
            if expr.operador == Operadores.SUBTRACAO:
                left = rec(expr.opEsq, current_fun)
                right = rec(expr.opDir, current_fun)
                return opBin_sub(left, right)
            if expr.operador == Operadores.MULTIPLIC:
                left = rec(expr.opEsq, current_fun)
                right = rec(expr.opDir, current_fun)
                return opBin_mul(left, right)
            if expr.operador == Operadores.DIVISAO:
                left = rec(expr.opEsq, current_fun)
                right = rec(expr.opDir, current_fun)
                return opBin_div(left, right)
            if expr.operador == Operadores.RESTO:
                left = rec(expr.opEsq, current_fun)
                right = rec(expr.opDir, current_fun)
                return opBin_mod(left, right)
            if expr.operador == Operadores.IGUAL_IGUAL:
                right = rec(expr.opDir, current_fun)
                left = rec(expr.opEsq, current_fun)
                return cmp_equal(right, left)
            if expr.operador == Operadores.MENOR:
                right = rec(expr.opDir, current_fun)
                left = rec(expr.opEsq, current_fun)
                return cmp_less(right, left)
            if expr.operador == Operadores.MAIOR:
                right = rec(expr.opDir, current_fun)
                left = rec(expr.opEsq, current_fun)
                return cmp_greater(right, left)
            if expr.operador == Operadores.MENOR_IGUAL:
                right = rec(expr.opDir, current_fun)
                left = rec(expr.opEsq, current_fun)
                return cmp_le(right, left)
            if expr.operador == Operadores.MAIOR_IGUAL:
                right = rec(expr.opDir, current_fun)
                left = rec(expr.opEsq, current_fun)
                return cmp_ge(right, left)
            if expr.operador == Operadores.DIFERENTE:
                right = rec(expr.opDir, current_fun)
                left = rec(expr.opEsq, current_fun)
                return cmp_ne(right, left)
            raise NotImplementedError(f"Operação {expr.operador} não suportada ainda")

        raise NotImplementedError(f"Nó desconhecido em rec(): {expr}")

    # gera código para statements (Assign, If, While, Block, Return)
    def gen_stmt(stmt, current_fun: FunDecl | None, func_return_label: str | None) -> str:
        # ReturnStmt
        if isinstance(stmt, ReturnStmt):
            code = rec(stmt.expr, current_fun)
            if func_return_label is not None:
                code += f"    jmp {func_return_label}\n"
            else:
                code += f"    jmp {exit_label}\n"
            return code

        # Assign
        if isinstance(stmt, Assign):
            code = rec(stmt.expr, current_fun)
            name = stmt.nome
            if current_fun is not None:
                local_offs = getattr(current_fun, 'local_offsets', {})
                param_offs = getattr(current_fun, 'param_offsets', {})
                if name in local_offs:
                    off = local_offs[name]
                    code += f"    mov %rax, {rbp_addr(off)}\n"
                    return code
                if name in param_offs:
                    off = param_offs[name]
                    code += f"    mov %rax, {rbp_addr(off)}\n"
                    return code
            code += f"    mov %rax, {name}(%rip)\n"
            return code

        # IfStmt
        if isinstance(stmt, IfStmt):
            l_false = new_label("Lfalso")
            l_end = new_label("Lfim")
            code = ""
            code += rec(stmt.cond, current_fun)
            code += "    cmp $0, %rax\n"
            code += f"    jz {l_false}\n"
            for s in stmt.then_stmts:
                code += gen_stmt(s, current_fun, func_return_label)
            code += f"    jmp {l_end}\n"
            code += f"{l_false}:\n"
            if stmt.else_stmts is not None:
                for s in stmt.else_stmts:
                    code += gen_stmt(s, current_fun, func_return_label)
            code += f"{l_end}:\n"
            return code

        # WhileStmt
        if isinstance(stmt, WhileStmt):
            l_begin = new_label("Linicio")
            l_end = new_label("Lfim")
            code = f"{l_begin}:\n"
            code += rec(stmt.cond, current_fun)
            code += "    cmp $0, %rax\n"
            code += f"    jz {l_end}\n"
            for s in stmt.body:
                code += gen_stmt(s, current_fun, func_return_label)
            code += f"    jmp {l_begin}\n"
            code += f"{l_end}:\n"
            return code

        # BlockStmt
        if isinstance(stmt, BlockStmt):
            code = ""
            for s in stmt.stmts:
                code += gen_stmt(s, current_fun, func_return_label)
            return code

        raise NotImplementedError(f"Stmt desconhecido em gen_stmt(): {stmt}")

    # rótulo de saída do main (_start) para tratar return no main
    exit_label = new_label("Lexit_main_")

    #Gerar código de cada função (fun_decls) ANTES de _start
    if isinstance(ast, Programa):
        for f in ast.fun_decls:
            # tornar visível
            asm += f".globl {f.nome}\n"
            asm += f"{f.nome}:\n"

            # prologue: salvar rbp, apontar rbp para o topo do frame e alocar espaço
            asm += "    push %rbp\n"
            asm += "    mov %rsp, %rbp\n"
            frame_size = getattr(f, 'frame_size', 0)
            if frame_size and frame_size > 0:
                asm += f"    sub ${frame_size}, %rsp\n"
            asm += "\n"

            # label de retorno da função (ponto comum para epílogo)
            func_ret_label = new_label(f"Lret_{f.nome}_")

            # inicializar declarações locais (em ordem)
            for d in f.local_decls:
                asm += rec(d.expr, f)       # resultado em %rax
                off = f.local_offsets.get(d.nome)
                if off is None:
                    raise RuntimeError(f"Offset da local '{d.nome}' não encontrado para função {f.nome}")
                asm += f"    mov %rax, {rbp_addr(off)}\n"

            # gerar comandos do corpo
            for c in f.comandos:
                asm += gen_stmt(c, f, func_ret_label)

            # gerar código para expressão de resultado (deixa %rax)
            asm += rec(f.resultado, f)
            # pular para epílogo comum (assim retornos internos também caem no epílogo)
            asm += f"    jmp {func_ret_label}\n\n"

            # epílogo
            asm += f"{func_ret_label}:\n"
            if frame_size and frame_size > 0:
                asm += f"    add ${frame_size}, %rsp\n"
            asm += "    pop %rbp\n"
            asm += "    ret\n\n"


    #inicializar variáveis globais e main com header()
    asm += header()

    if isinstance(ast, Programa):
        for d in ast.var_decls:
            asm += rec(d.expr, None)
            asm += f"    mov %rax, {d.nome}(%rip)\n"
    asm += "\n"

    asm += "    push %rbp\n"
    asm += "    mov %rsp, %rbp\n\n"

    if isinstance(ast, Programa):
        for c in ast.comandos:
            asm += gen_stmt(c, None, None)
        asm += rec(ast.resultado, None)
    else:
        asm += rec(ast, None)

    # inserir label de saída do main (para returns do main saltarem para cá)
    asm += f"{exit_label}:\n\n"

    # chama o footer (imprime_num e sair do professor)
    asm += footer()

    # adicionar nova linha extra no final para evitar warning de EOF (Não sei pq está dando isso)
    asm += "\n"

    return asm