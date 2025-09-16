# João Victor Lourenço da Silva (20220005997)

from enum import Enum, auto

class Numero(Enum):
    NUMERO = auto()

class Operadores(Enum):
    SOMA = auto()
    SUBTRACAO = auto()
    MULTIPLIC = auto()
    DIVISAO = auto()
    MENOR = auto()
    MAIOR = auto()
    IGUAL_IGUAL = auto()

class Pontuacao(Enum):
    PAREN_ESQ = auto()
    PAREN_DIR = auto()
    EOF = auto()
    IGUAL = auto() 
    PONTO_VIRGULA = auto()
    CHAVE_ESQ = auto()
    CHAVE_DIR = auto()     

class Identificador(Enum):
    IDENT = auto()

class PalavraReservada(Enum):
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()

class Error(Enum):
    LEX_ERROR = auto()
