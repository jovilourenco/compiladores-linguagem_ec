# João Victor Lourenço da Silva (20220005997)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from .token_tipos import Operadores  # reutiliza os operadores

class Exp(ABC):

    @abstractmethod
    def avaliador(self, env: Optional[Dict[str, int]] = None) -> int:
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
        # nunca deve chegar aqui, na teoria
        raise ValueError(f"Operador desconhecido: {self.operador}")

    def gerador(self) -> str:
        # Imprime na forma (esq operador dir)
        op_map = {
            Operadores.SOMA: '+',
            Operadores.SUBTRACAO: '-',
            Operadores.MULTIPLIC: '*',
            Operadores.DIVISAO: '/',
        }
        simb = op_map.get(self.operador, '?')
        return f"({self.opEsq.gerador()} {simb} {self.opDir.gerador()})"

@dataclass
class Decl:
    """Declaração: nome = expr; (armazenamos linha/pos para mensagens de erro se necessário)"""
    nome: str
    expr: Exp
    linha: Optional[int] = None
    pos: Optional[int] = None

    def __repr__(self) -> str:
        return f"Decl({self.nome} = {self.expr})"

    def gerador(self) -> str:
        return f"{self.nome} = {self.expr.gerador()};"

@dataclass
class Programa:
    """Raiz: lista de declarações + expressão final."""
    declaracoes: List[Decl]
    resultado: Exp

    def gerador(self) -> str:
        parts = []
        for d in self.declaracoes:
            parts.append(d.gerador())
        parts.append(f"= {self.resultado.gerador()}")
        return "\n".join(parts)

    def avaliador(self) -> int:
        """
        Avalia todo o programa:
        - Processa declarações na ordem, atualiza ambiente (dict)
        - Avalia expressão final no ambiente resultante
        - Se houver uso de variável não declarada, Var.avaliador já lança NameError com linha/pos
        """
        env: Dict[str, int] = {}
        for d in self.declaracoes:
            val = d.expr.avaliador(env)
            env[d.nome] = val
        return self.resultado.avaliador(env)

    def __repr__(self) -> str:
        return f"Programa(decls={self.declaracoes}, result={self.resultado})"