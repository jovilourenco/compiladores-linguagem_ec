# João Victor Lourenço da Silva (20220005997)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional
from .token_tipos import Operadores  # reutiliza os operadores

class Exp(ABC):

    @abstractmethod
    def avaliador(self, env: Optional[Dict[str, int]] = None) -> int: #avaliador, agora, recebe env (tabela de símbolos)
        # Obj: Interpreta e retorna o valor da expressão.
        pass

    @abstractmethod
    def gerador(self) -> str:
        # Obj: Gera a representação textual da expressão EC1.
        pass

@dataclass
class Const(Exp):
    valor: int

    def avaliador(self, env: Optional[Dict[str, int]] = None) -> int:
        # Nós constantes avaliadorm para seu próprio valor
        return self.valor

    def gerador(self) -> str:
        # Impressão de literal é apenas o número
        return str(self.valor)

@dataclass
class Var(Exp):
    nome: str
    linha: Optional[int] = None
    pos: Optional[int] = None

    def avaliador(self, env: Optional[Dict[str, int]] = None) -> int:
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
class OpBin(Exp):
    operador: Operadores
    opEsq: Exp
    opDir: Exp

    def avaliador(self, env: Optional[Dict[str, int]] = None) -> int:
        # Avaliador recursivamente os operandos e aplica a operação
        esquerda = self.opEsq.avaliador(env)
        direita = self.opDir.avaliador(env)
        if self.operador == Operadores.SOMA:
            return esquerda + direita
        if self.operador == Operadores.SUBTRACAO:
            return esquerda - direita
        if self.operador == Operadores.MULTIPLIC:
            return esquerda * direita
        if self.operador == Operadores.DIVISAO:
            if direita == 0:
                raise ZeroDivisionError("Divisão por zero")
            return esquerda // direita  # divisão inteira
        if self.operador == Operadores.MENOR:
            return 1 if esquerda < direita else 0
        if self.operador == Operadores.MAIOR:
            return 1 if esquerda > direita else 0
        if self.operador == Operadores.IGUAL_IGUAL:
            return 1 if esquerda == direita else 0
        # nunca deve chegar aqui, na teoria
        raise ValueError(f"Operador desconhecido: {self.operador}")

    def gerador(self) -> str:
        # Imprime na forma (esq operador dir)
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

@dataclass
class Decl:
    #Declaração: nome = expr; (armazenamos linha/pos para mensagens de erro se necessário)
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

    def avaliador(self, env: Dict[str, int]) -> None:
        # Regra semântica: o nome já deve estar declarado no ambiente.
        if self.nome not in env:
            ln = self.linha if self.linha is not None else '?'
            ps = self.pos if self.pos is not None else '?'
            raise NameError(f"Erro semântico: atribuição para variável não declarada '{self.nome}' (linha {ln}, pos {ps})")
        # Evalua o lado direito (RHS) — Var.avaliador já verifica usos não declarados no RHS.
        val = self.expr.avaliador(env)
        env[self.nome] = val
        return None

@dataclass
class IfStmt(Stmt):
    cond: Exp
    then_stmts: List[Stmt]
    else_stmts: Optional[List[Stmt]] = None
    def __repr__(self) -> str:
        return f"If(cond={self.cond}, then={self.then_stmts}, else={self.else_stmts})"
    def avaliador(self, env: Dict[str, int]) -> None:
        cond_val = self.cond.avaliador(env)
        if cond_val != 0:
            for s in self.then_stmts:
                s.avaliador(env)
        else:
            if self.else_stmts is not None:
                for s in self.else_stmts:
                    s.avaliador(env)
        return None

@dataclass
class WhileStmt(Stmt):
    cond: Exp
    body: List[Stmt]
    def __repr__(self) -> str:
        return f"While(cond={self.cond}, body={self.body})"
    def avaliador(self, env: Dict[str, int]) -> None:
        while self.cond.avaliador(env) != 0:
            for s in self.body:
                s.avaliador(env)
        return None
    
@dataclass
class BlockStmt(Stmt):
    """Bloco composto: lista de statements executados em sequência."""
    stmts: List[Stmt]

    def __repr__(self) -> str:
        return f"Block({self.stmts})"

    def avaliador(self, env: Dict[str, int]) -> None:
        # executa cada statement na ordem (mesmo ambiente)
        for s in self.stmts:
            s.avaliador(env)
        return None

@dataclass
class Programa: # Programa é, de fato, a lista de declarações e o resultado (expressão a ser processada)
    declaracoes: List[Decl]
    comandos: List[Stmt]
    resultado: Exp

    def verifica_semantica(self) -> None:
        """
        Verificação semântica estática:
        - percorre declarações em ordem, verificando que cada expressão usa apenas variáveis já declaradas;
        - ao finalizar checa comandos e a expressão de retorno;
        - levanta NameError na primeira violação encontrada.
        """
        # tabela de símbolos simples: nomes declarados
        env: Dict[str, int] = {}

        # função auxiliar para verificar uma expressão quanto ao uso de Vars
        def check_expr(e: Exp):
            if isinstance(e, Var):
                if e.nome not in env:
                    ln = e.linha if e.linha is not None else '?'
                    ps = e.pos if e.pos is not None else '?'
                    raise NameError(f"Erro semântico: variável '{e.nome}' não declarada (linha {ln}, pos {ps})")
            elif isinstance(e, OpBin):
                check_expr(e.opEsq)
                check_expr(e.opDir)
            elif isinstance(e, Const):
                return
            else:
                # caso apareça algum nó novo de Exp no futuro, tratar aqui
                return

        # 1) verificar declarações na ordem (uma declaração pode usar nomes declarados anteriormente)
        for d in self.declaracoes:
            check_expr(d.expr)
            # depois de checar a expressão, a declaração inclui novo nome no env
            env[d.nome] = 0  # valor simbólico, só interessa o nome

        # função auxiliar para verificar statements/comandos
        def check_stmt(s: Stmt):
            # Assign: LHS deve já existir e RHS não deve usar nomes não declarados
            if isinstance(s, Assign):
                if s.nome not in env:
                    ln = s.linha if s.linha is not None else '?'
                    ps = s.pos if s.pos is not None else '?'
                    raise NameError(f"Erro semântico: atribuição para variável não declarada '{s.nome}' (linha {ln}, pos {ps})")
                check_expr(s.expr)
            elif isinstance(s, IfStmt):
                check_expr(s.cond)
                for ss in s.then_stmts:
                    check_stmt(ss)
                if s.else_stmts is not None:
                    for ss in s.else_stmts:
                        check_stmt(ss)
            elif isinstance(s, WhileStmt):
                check_expr(s.cond)
                for ss in s.body:
                    check_stmt(ss)
            elif hasattr(s, 'stmts'):  # BlockStmt (composto)
                for ss in s.stmts:
                    check_stmt(ss)
            else:
                # outros tipos de Stmt (se houver) - por enquanto nada
                return

        # 2) verificar os comandos (em ordem)
        for c in self.comandos:
            check_stmt(c)

        # 3) verificar expressão de retorno
        check_expr(self.resultado)

        # se chegou até aqui, passa na verificação semântica
        return None

    def gerador(self) -> str:
        parts = []
        for d in self.declaracoes:
            parts.append(d.gerador())
        for c in self.comandos:
            parts.append(str(c))
        parts.append(f"return {self.resultado.gerador()};")
        return "\n".join(parts)

    def avaliador(self) -> int:
        env: Dict[str, int] = {}
        for d in self.declaracoes:
            val = d.expr.avaliador(env)
            env[d.nome] = val
        for c in self.comandos:
            c.avaliador(env)
        return self.resultado.avaliador(env)

    def __repr__(self) -> str:
        return f"Programa(decls={self.declaracoes}, cmds={self.comandos}, result={self.resultado})"