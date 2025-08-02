# João Victor Lourenço da Silva (20220005997)

from token_tipos import Numero, Operadores, Pontuacao, Error

class Token:
    def __init__(self, tipo, lexema: str, pos: int):
        # tipo pode ser membro de Numero, Operadores ou Pontuacao
        self.tipo = tipo
        self.lexema = lexema
        self.pos = pos

    def __repr__(self): # padrão de exibição do token
        return f"<{self.tipo.__class__.__name__}.{self.tipo.name}, '{self.lexema}', pos={self.pos}>"
