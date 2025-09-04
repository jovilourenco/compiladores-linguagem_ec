# João Victor Lourenço da Silva (20220005997)

from enum import Enum, auto

class Numero(Enum):
    NUMERO = auto()

class Operadores(Enum):
    SOMA = auto()
    SUBTRACAO = auto()
    MULTIPLIC = auto()
    DIVISAO = auto()

class Pontuacao(Enum):
    PAREN_ESQ = auto()
    PAREN_DIR = auto()
    EOF = auto()
    IGUAL = auto()            # '=' (atribuição e inicio do resultado)
    PONTO_VIRGULA = auto()   # ';'

class Identificador(Enum):
    IDENT = auto()

class Error(Enum):
    LEX_ERROR = auto()
