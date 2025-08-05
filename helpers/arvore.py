# João Victor Lourenço da Silva (20220005997)

from abc import ABC, abstractmethod
from dataclasses import dataclass
from .token_tipos import Operadores  # reutiliza os operadores

class Exp(ABC):

    @abstractmethod
    def avaliador(self) -> int:
        # Obj: Interpreta e retorna o valor da expressão.
        pass

    @abstractmethod
    def gerador(self) -> str:
        # Obj: Gera a representação textual da expressão EC1.
        pass

@dataclass
class Const(Exp):
    valor: int

    def avaliador(self) -> int:
        # Nós constantes avaliadorm para seu próprio valor
        return self.valor

    def gerador(self) -> str:
        # Impressão de literal é apenas o número
        return str(self.valor)

@dataclass
class OpBin(Exp):
    operador: Operadores
    opEsq: Exp
    opDir: Exp

    def avaliador(self) -> int:
        # Avaliador recursivamente os operandos e aplica a operação
        esquerda = self.opEsq.avaliador()
        direita = self.opDir.avaliador()
        if self.operador == Operadores.SOMA:
            return esquerda + direita
        if self.operador == Operadores.SUBTRACAO:
            return esquerda - direita
        if self.operador == Operadores.MULTIPLIC:
            return esquerda * direita
        if self.operador == Operadores.DIVISAO:
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

