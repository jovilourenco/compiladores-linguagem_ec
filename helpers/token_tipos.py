# João Victor Lourenço da Silva (20220005997)

from enum import Enum, auto

class Numero(Enum):
    NUMERO = auto()

class Operadores(Enum):
    SOMA = auto()
    SUBTRACAO = auto()
    MULTIPLIC = auto()
    DIVISAO = auto()
    RESTO = auto()
    ADDEQ = auto()       
    SUBEQ = auto()      
    MULEQ = auto()       
    DIVEQ = auto()       
    INC = auto()         
    DEC = auto()         
    MENOR = auto()
    MAIOR = auto()
    MENOR_IGUAL = auto()
    MAIOR_IGUAL = auto()
    DIFERENTE = auto()
    IGUAL_IGUAL = auto()

class Pontuacao(Enum):
    PAREN_ESQ = auto()
    PAREN_DIR = auto()
    EOF = auto()
    IGUAL = auto() 
    PONTO_VIRGULA = auto()
    CHAVE_ESQ = auto()
    CHAVE_DIR = auto()
    VIRGULA = auto() 

class Identificador(Enum):
    IDENT = auto()

class PalavraReservada(Enum):
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    RETURN = auto()
    FUN = auto()
    VAR = auto()
    MAIN = auto()

class Error(Enum):
    LEX_ERROR = auto()
