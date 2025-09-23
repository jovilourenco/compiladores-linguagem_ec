# João Victor Lourenço da Silva (20220005997)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from .token_tipos import Operadores  # reutiliza os operadores

class Exp(ABC):
    @abstractmethod
    def avaliador(self, env: Optional[Dict[str, int]] = None, funcoes: Optional[Dict[str, "FunDecl"]] = None) -> int:
        # interpreta e retorna o valor da expressão.
        pass

    @abstractmethod
    def gerador(self) -> str:
        pass

@dataclass
class Const(Exp):
    valor: int

    def avaliador(self, env: Optional[Dict[str, int]] = None, funcoes: Optional[Dict[str, "FunDecl"]] = None) -> int:
        return self.valor

    def gerador(self) -> str:
        return str(self.valor)

@dataclass
class Var(Exp):
    nome: str
    linha: Optional[int] = None
    pos: Optional[int] = None

    def avaliador(self, env: Optional[Dict[str, int]] = None, funcoes: Optional[Dict[str, "FunDecl"]] = None) -> int:
        if env is None:
            env = {}
        if self.nome not in env:
            ln = self.linha if self.linha is not None else '?'
            ps = self.pos if self.pos is not None else '?'
            raise NameError(f"Erro semântico: variável '{self.nome}' não declarada (linha {ln}, pos {ps})")
        return env[self.nome]

    def gerador(self) -> str:
        return self.nome

@dataclass
class Call(Exp):
    nome: str
    args: List[Exp]
    linha: Optional[int] = None
    pos: Optional[int] = None

    def __repr__(self) -> str:
        return f"Call({self.nome}({', '.join(map(str, self.args))}))"

    def avaliador(self, env: Optional[Dict[str, int]] = None, funcoes: Optional[Dict[str, "FunDecl"]] = None) -> int:
        if funcoes is None or self.nome not in funcoes:
            ln = self.linha if self.linha is not None else '?'
            ps = self.pos if self.pos is not None else '?'
            raise NameError(f"Erro semântico: chamada para função não declarada '{self.nome}' (linha {ln}, pos {ps})")
        f = funcoes[self.nome]
        # avaliar argumentos no ambiente atual
        args_vals = [a.avaliador(env, funcoes) for a in self.args]
        if len(args_vals) != len(f.params):
            raise TypeError(f"Erro semântico: chamada para '{self.nome}' com número errado de argumentos (esperado {len(f.params)}, encontrado {len(args_vals)})")
        # criar ambiente local como cópia do env (isolamento)
        global_env = dict(env) if env is not None else {}
        local_env = dict(global_env)  # alterações locais não afetam o env original
        # atribuir parâmetros
        for pname, val in zip(f.params, args_vals):
            local_env[pname] = val
        # avaliar declarações locais da função (em ordem)
        for d in f.local_decls:
            local_env[d.nome] = d.expr.avaliador(local_env, funcoes)
        # executar comandos
        try:
            for s in f.comandos:
                s.avaliador(local_env, funcoes)
        except ReturnException as re:
            return re.value
        # se não houve return precoce (por segurança), avaliar resultado da função
        return f.resultado.avaliador(local_env, funcoes)

    def gerador(self) -> str:
        args_s = ", ".join([a.gerador() for a in self.args])
        return f"{self.nome}({args_s})"

@dataclass
class OpBin(Exp):
    operador: Operadores
    opEsq: Exp
    opDir: Exp

    def avaliador(self, env: Optional[Dict[str, int]] = None, funcoes: Optional[Dict[str, "FunDecl"]] = None) -> int:
        esquerda = self.opEsq.avaliador(env, funcoes)
        direita = self.opDir.avaliador(env, funcoes)
        if self.operador == Operadores.SOMA:
            return esquerda + direita
        if self.operador == Operadores.SUBTRACAO:
            return esquerda - direita
        if self.operador == Operadores.MULTIPLIC:
            return esquerda * direita
        if self.operador == Operadores.DIVISAO:
            if direita == 0:
                raise ZeroDivisionError("Divisão por zero")
            return esquerda // direita
        if self.operador == Operadores.MENOR:
            return 1 if esquerda < direita else 0
        if self.operador == Operadores.MAIOR:
            return 1 if esquerda > direita else 0
        if self.operador == Operadores.IGUAL_IGUAL:
            return 1 if esquerda == direita else 0
        raise ValueError(f"Operador desconhecido: {self.operador}")

    def gerador(self) -> str:
        op_map = {
            Operadores.SOMA: '+',
            Operadores.SUBTRACAO: '-',
            Operadores.MULTIPLIC: '*',
            Operadores.DIVISAO: '/',
            Operadores.MENOR: '<',
            Operadores.MAIOR: '>',
            Operadores.IGUAL_IGUAL: '==',
        }
        simb = op_map.get(self.operador, '?')
        return f"({self.opEsq.gerador()} {simb} {self.opDir.gerador()})"

# ---------- Declarações e Stmts ----------
@dataclass
class Decl:
    nome: str
    expr: Exp
    linha: Optional[int] = None
    pos: Optional[int] = None

    def __repr__(self) -> str:
        return f"Decl({self.nome} = {self.expr})"

    def gerador(self) -> str:
        return f"{self.nome} = {self.expr.gerador()};"

@dataclass
class Stmt:
    pass

@dataclass
class Assign(Stmt):
    nome: str
    expr: Exp
    linha: Optional[int] = None
    pos: Optional[int] = None

    def __repr__(self) -> str:
        return f"Assign({self.nome} = {self.expr})"

    def avaliador(self, env: Dict[str, int], funcoes: Optional[Dict[str, "FunDecl"]] = None) -> None:
        if self.nome not in env:
            ln = self.linha if self.linha is not None else '?'
            ps = self.pos if self.pos is not None else '?'
            raise NameError(f"Erro semântico: atribuição para variável não declarada '{self.nome}' (linha {ln}, pos {ps})")
        val = self.expr.avaliador(env, funcoes)
        env[self.nome] = val
        return None

@dataclass
class IfStmt(Stmt):
    cond: Exp
    then_stmts: List[Stmt]
    else_stmts: Optional[List[Stmt]] = None

    def __repr__(self) -> str:
        return f"If(cond={self.cond}, then={self.then_stmts}, else={self.else_stmts})"

    def avaliador(self, env: Dict[str, int], funcoes: Optional[Dict[str, "FunDecl"]] = None) -> None:
        cond_val = self.cond.avaliador(env, funcoes)
        if cond_val != 0:
            for s in self.then_stmts:
                s.avaliador(env, funcoes)
        else:
            if self.else_stmts is not None:
                for s in self.else_stmts:
                    s.avaliador(env, funcoes)
        return None

@dataclass
class WhileStmt(Stmt):
    cond: Exp
    body: List[Stmt]

    def __repr__(self) -> str:
        return f"While(cond={self.cond}, body={self.body})"

    def avaliador(self, env: Dict[str, int], funcoes: Optional[Dict[str, "FunDecl"]] = None) -> None:
        while self.cond.avaliador(env, funcoes) != 0:
            for s in self.body:
                s.avaliador(env, funcoes)
        return None

@dataclass
class BlockStmt(Stmt):
    stmts: List[Stmt]

    def __repr__(self) -> str:
        return f"Block({self.stmts})"

    def avaliador(self, env: Dict[str, int], funcoes: Optional[Dict[str, "FunDecl"]] = None) -> None:
        for s in self.stmts:
            s.avaliador(env, funcoes)
        return None

class ReturnException(Exception):
    def __init__(self, value: int):
        super().__init__("Return")
        self.value = value

@dataclass
class ReturnStmt(Stmt):
    expr: Exp
    linha: Optional[int] = None
    pos: Optional[int] = None

    def __repr__(self) -> str:
        return f"Return({self.expr})"

    def avaliador(self, env: Dict[str, int], funcoes: Optional[Dict[str, "FunDecl"]] = None) -> None:
        val = self.expr.avaliador(env, funcoes)
        raise ReturnException(val)

# ---------- Função (decl) ----------
@dataclass
class FunDecl:
    nome: str
    params: List[str]
    local_decls: List[Decl]
    comandos: List[Stmt]
    resultado: Exp
    linha: Optional[int] = None
    pos: Optional[int] = None

    def __repr__(self) -> str:
        return f"FunDecl({self.nome}({', '.join(self.params)}))"

    def gerador(self) -> str:
        params = ", ".join(self.params)
        decls = "\n".join([d.gerador() for d in self.local_decls])
        cmds = "\n".join([str(c) for c in self.comandos])
        return f"fun {self.nome}({params}) {{\n{decls}\n{cmds}\nreturn {self.resultado.gerador()};\n}}"

# ---------- PROGRAMA ----------
@dataclass
class Programa:
    var_decls: List[Decl]          # variáveis globais (top-level var)
    fun_decls: List[FunDecl]       # funções
    comandos: List[Stmt]           # comandos do main
    resultado: Exp                 # expressão final (return do main ou Const(0) se ausente)

    def __repr__(self) -> str:
        return f"Programa(vars={self.var_decls}, funs={self.fun_decls}, cmds={self.comandos}, result={self.resultado})"

    def verifica_semantica(self) -> None:
        """
        Verificação semântica:
        - constrói tabela de símbolos para variáveis globais e funções (em ordem)
        - verifica duplicatas
        - verifica que funções chamam apenas funções já declaradas anteriormente (evita recursão mútua/forward)
        - verifica corpos (decls locais, comandos, expressão de retorno)
        - verifica que main não contém 'var' (o parser já evita, mas checagem extra)
        """
        env: Dict[str, int] = {}
        funs: Dict[str, FunDecl] = {}

        # 1) processar var_decls (globais)
        for d in self.var_decls:
            # checar expr usa apenas nomes já declarados (ex.: não permite forward ref a variáveis)
            def check_e(e: Exp):
                if isinstance(e, Var):
                    if e.nome not in env:
                        ln = e.linha if e.linha is not None else '?'
                        ps = e.pos if e.pos is not None else '?'
                        raise NameError(f"Erro semântico: variável '{e.nome}' não declarada (linha {ln}, pos {ps})")
                elif isinstance(e, OpBin):
                    check_e(e.opEsq)
                    check_e(e.opDir)
                elif isinstance(e, Call):
                    # chamada a função ainda não permitida aqui (ou precisa existir); permitimos chamadas para funções já em funs
                    if e.nome not in funs:
                        ln = e.linha if e.linha is not None else '?'
                        ps = e.pos if e.pos is not None else '?'
                        raise NameError(f"Erro semântico: chamada para função não declarada '{e.nome}' (linha {ln}, pos {ps})")
                    for arg in e.args:
                        check_e(arg)
                else:
                    return
            check_e(d.expr)
            if d.nome in env:
                raise NameError(f"Erro semântico: variável '{d.nome}' já declarada")
            env[d.nome] = 0

        # 2) processar funções (registrar assinaturas em ordem)
        for f in self.fun_decls:
            if f.nome in funs:
                raise NameError(f"Erro semântico: função '{f.nome}' já declarada")
            funs[f.nome] = f  # registramos; mas para evitar mutual recursion, vamos checar corpos permitindo apenas chamadas para funções já presentes antes
            # Nota: não checamos corpo aqui para permitir referências só a funções já registradas (a checagem detalhada vem abaixo)

        # 3) checar corpos das funções (evitar chamadas para funções que aparecem depois -> evita mutual recursion)
        # Para isso, nós percorreremos as funções em ordem e construiremos uma tabela parcial
        partial_funs: Dict[str, FunDecl] = {}
        for f in self.fun_decls:
            # duplicata de nome com variáveis?
            if f.nome in env:
                raise NameError(f"Erro semântico: nome '{f.nome}' usado por variável e função")
            # verificar corpo: os usos de Var devem estar em env OU em params OU em local_decls conforme ordem
            # construir env local inicial com parâmetros (nome->0) + _global env
            local_env = dict(env)
            for p in f.params:
                if p in local_env:
                    raise NameError(f"Erro semântico: parâmetro '{p}' em função '{f.nome}' conflita com nome já declarado")
                local_env[p] = 0
            # verificar declarações locais (cada inicializador pode usar nomes já no local_env)
            for d in f.local_decls:
                # verificar expressão de inicialização
                def check_e2(e: Exp):
                    if isinstance(e, Var):
                        if e.nome not in local_env:
                            ln = e.linha if e.linha is not None else '?'
                            ps = e.pos if e.pos is not None else '?'
                            raise NameError(f"Erro semântico: variável '{e.nome}' não declarada (linha {ln}, pos {ps})")
                    elif isinstance(e, OpBin):
                        check_e2(e.opEsq); check_e2(e.opDir)
                    elif isinstance(e, Call):
                        # permitir chamadas para a própria função (recursão direta)
                        # ou para funções já registradas em partial_funs (funções anteriores)
                        if e.nome != f.nome and e.nome not in partial_funs:
                            ln = e.linha if e.linha is not None else '?'
                            ps = e.pos if e.pos is not None else '?'
                            raise NameError(f"Erro semântico: chamada para função não disponível ainda '{e.nome}' (linha {ln}, pos {ps})")
                        for arg in e.args:
                            check_e2(arg)
                    else:
                        return
                check_e2(d.expr)
                # depois de checar, adicionar o nome local
                if d.nome in local_env:
                    raise NameError(f"Erro semântico: variável local '{d.nome}' redeclarada em função '{f.nome}'")
                local_env[d.nome] = 0
            # verificar comandos do corpo
            def check_stmt(s: Stmt):
                if isinstance(s, Assign):
                    if s.nome not in local_env:
                        ln = s.linha if s.linha is not None else '?'
                        ps = s.pos if s.pos is not None else '?'
                        raise NameError(f"Erro semântico: atribuição para variável não declarada '{s.nome}' (linha {ln}, pos {ps})")
                    # verificar RHS
                    check_e2(s.expr)
                elif isinstance(s, IfStmt):
                    check_e2(s.cond)
                    for ss in s.then_stmts: check_stmt(ss)
                    if s.else_stmts is not None:
                        for ss in s.else_stmts: check_stmt(ss)
                elif isinstance(s, WhileStmt):
                    check_e2(s.cond)
                    for ss in s.body: check_stmt(ss)
                elif isinstance(s, ReturnStmt):
                    check_e2(s.expr)
                elif isinstance(s, BlockStmt):
                    for ss in s.stmts: check_stmt(ss)
                else:
                    return
            for c in f.comandos:
                check_stmt(c)
            # verificar expressão de retorno da função
            def check_e3(e: Exp):
                if isinstance(e, Var):
                    if e.nome not in local_env:
                        ln = e.linha if e.linha is not None else '?'
                        ps = e.pos if e.pos is not None else '?'
                        raise NameError(f"Erro semântico: variável '{e.nome}' não declarada (linha {ln}, pos {ps})")
                elif isinstance(e, OpBin):
                    check_e3(e.opEsq); check_e3(e.opDir)
                elif isinstance(e, Call):
                    # permitir recursão direta (chamar a própria função) ou chamadas para funções já em partial_funs
                    if e.nome != f.nome and e.nome not in partial_funs:
                        ln = e.linha if e.linha is not None else '?'
                        ps = e.pos if e.pos is not None else '?'
                        raise NameError(f"Erro semântico: chamada para função não disponível ainda '{e.nome}' (linha {ln}, pos {ps})")
                    for arg in e.args: check_e3(arg)
                else:
                    return
            check_e3(f.resultado)
            # depois de tudo OK, registramos f em partial_funs para funções posteriores poderem chamá-la
            partial_funs[f.nome] = f

        # 4) verificar comandos do main (os nomes usados devem estar em env (globais) ou em funções via chamadas)
        # main não deve conter var (parser já impede); aqui checamos usos de Var e de chamadas
        def check_expr_main(e: Exp):
            if isinstance(e, Var):
                if e.nome not in env:
                    ln = e.linha if e.linha is not None else '?'
                    ps = e.pos if e.pos is not None else '?'
                    raise NameError(f"Erro semântico: variável '{e.nome}' não declarada (linha {ln}, pos {ps})")
            elif isinstance(e, OpBin):
                check_expr_main(e.opEsq); check_expr_main(e.opDir)
            elif isinstance(e, Call):
                if e.nome not in partial_funs:
                    ln = e.linha if e.linha is not None else '?'
                    ps = e.pos if e.pos is not None else '?'
                    raise NameError(f"Erro semântico: chamada para função não declarada '{e.nome}' (linha {ln}, pos {ps})")
                for arg in e.args: check_expr_main(arg)
            else:
                return

        def check_stmt_main(s: Stmt):
            if isinstance(s, Assign):
                if s.nome not in env:
                    ln = s.linha if s.linha is not None else '?'
                    ps = s.pos if s.pos is not None else '?'
                    raise NameError(f"Erro semântico: atribuição para variável não declarada '{s.nome}' (linha {ln}, pos {ps})")
                check_expr_main(s.expr)
            elif isinstance(s, IfStmt):
                check_expr_main(s.cond)
                for ss in s.then_stmts: check_stmt_main(ss)
                if s.else_stmts is not None:
                    for ss in s.else_stmts: check_stmt_main(ss)
            elif isinstance(s, WhileStmt):
                check_expr_main(s.cond)
                for ss in s.body: check_stmt_main(ss)
            elif isinstance(s, ReturnStmt):
                check_expr_main(s.expr)
            elif isinstance(s, BlockStmt):
                for ss in s.stmts: check_stmt_main(ss)
            else:
                return

        for c in self.comandos:
            check_stmt_main(c)
        check_expr_main(self.resultado)

        # se chegou até aqui, passou na verificação semântica
        return None

    def gerador(self) -> str:
        parts = []
        for d in self.var_decls:
            parts.append(d.gerador())
        for f in self.fun_decls:
            parts.append(f.gerador())
        for c in self.comandos:
            parts.append(str(c))
        parts.append(f"return {self.resultado.gerador()};")
        return "\n".join(parts)

    def avaliador(self) -> int:
        # monta env global e tabela de funções (em ordem)
        env: Dict[str, int] = {}
        funcs: Dict[str, FunDecl] = {}
        # var_decls
        for d in self.var_decls:
            val = d.expr.avaliador(env, funcs)
            env[d.nome] = val
        # funções (registrar em tabela na ordem)
        for f in self.fun_decls:
            if f.nome in funcs:
                raise NameError(f"Erro semântico: função '{f.nome}' já declarada")
            funcs[f.nome] = f
        # executar comandos do main
        try:
            for c in self.comandos:
                c.avaliador(env, funcs)
        except ReturnException as re:
            return re.value
        # avaliar resultado final
        return self.resultado.avaliador(env, funcs)
