# João Victor Lourenço da Silva (20220005997)

from typing import List
from lex_token import Token
from token_tipos import Numero, Operadores, Pontuacao, Error
from arvore import Exp, Const, OpBin

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0  # posição atual no array de tokens

    def get(self) -> Token:
        # retorna o token atual ou None no fim
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def proximo_token(self):
        # avança para o próximo token
        if self.pos < len(self.tokens):
            self.pos += 1

    def verificaProxToken(self, tipo_esperado) -> Token: # Recebe o tipo que deve vir no próximo token.
        tok = self.get()
        if tok is None or tok.tipo != tipo_esperado:
            pos = tok.pos if tok else self.pos
            raise ParserError(
                f"Erro sintático na posição {pos}: esperado {tipo_esperado}, encontrado {tok}"
            )
        self.proximo_token()
        return tok

    def analisaOperador(self) -> Operadores:
        # Só verificar se realmente é um operador
        tok = self.get()
        if tok is None or tok.tipo not in (
            Operadores.SOMA, Operadores.SUBTRACAO,
            Operadores.MULTIPLIC, Operadores.DIVISAO
        ):
            pos = tok.pos if tok else self.pos
            raise ParserError(
                f"Erro sintático na posição {pos}: operador esperado, encontrado {tok}"
            )
        operador = tok.tipo
        self.proximo_token()
        return operador

    def analisaExp(self) -> Exp:
        tok = self.get()
        if tok is None:
            raise ParserError("Fim inesperado de entrada ao analisar expressão")

        # caso literal inteiro
        if tok.tipo == Numero.NUMERO:
            self.proximo_token()
            valor = int(tok.lexema)
            return Const(valor)

        # caso expressão entre parênteses
        if tok.tipo == Pontuacao.PAREN_ESQ:
            self.proximo_token()  # consome '('
            # analisa primeira subexpressão
            opEsq = self.analisaExp()
            # analisa operador
            operador = self.analisaOperador()
            # analisa segunda subexpressão
            opDir = self.analisaExp()
            # verifica fechamento
            self.verificaProxToken(Pontuacao.PAREN_DIR)
            return OpBin(operador, opEsq, opDir)

        # nenhum caso válido
        raise ParserError(
            f"Erro sintático na posição {tok.pos}: expressão inválida, token {tok}"
        )

    def parse(self) -> Exp:
        ast = self.analisaExp()
        # depois da expressão deve vir EOF
        self.verificaProxToken(Pontuacao.EOF)
        return ast


if __name__ == '__main__':
    import sys
    from analisadorLexicoEC import AnalizadorLexico # Primeiro faz a análise léxica

    if len(sys.argv) != 2:
        print("Uso: python analisadorSintaticoEC.py <arquivo.txt>")
        sys.exit(1)

    # Análise Léxica
    with open(sys.argv[1], 'r') as f:
        texto = f.read()
    lexer = AnalizadorLexico(texto)
    tokens = lexer.tokenizador()

    # Análise Sintática
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except ParserError as e:
        print(e)
        sys.exit(1)

    # Resultado da análise descendente recursiva
    print("Resultado da análise sintática:", ast)

    # impressão da expressão a partir da árvore 
    expr_str = ast.gerador()
    print("Expressão parseada:", expr_str)

    # Interpretação (resultado da expressão)
    resultado = ast.avaliador()
    print("Resultado da avaliação:", resultado)