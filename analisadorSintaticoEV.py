# João Victor Lourenço da Silva (20220005997)

from typing import List

from helpers.token import Token
from helpers.token_tipos import Numero, Identificador, Operadores, Pontuacao, Error
from helpers.arvore import Exp, Const, OpBin, Var, Decl, Programa

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
        # Verifica que o token atual é do tipo esperado e o consome;
        tok = self.get()
        if tok is None or tok.tipo != tipo_esperado:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(
                f"Erro sintático na linha {linha}, pos {pos}: esperado {tipo_esperado}, encontrado {tok}"
            )
        self.proximo_token()
        return tok

    # -------------------------
    # prim -> número | '(' exp_a ')'
    # -------------------------
    def analisaPrim(self) -> Exp:
        tok = self.get()
        if tok is None: # Se houve algum erro
            raise ParserError("Fim inesperado de entrada ao analisar primária")

        if tok.tipo == Numero.NUMERO:
            self.proximo_token()
            valor = int(tok.lexema)
            return Const(valor)
        
        if tok.tipo == Identificador.IDENT:
            # se for identificador, tem que criar uma Var (com info de linha/pos para erros semânticos)
            nome = tok.lexema
            linha = tok.linha
            pos = tok.pos
            self.proximo_token()
            return Var(nome, linha=linha, pos=pos)

        if tok.tipo == Pontuacao.PAREN_ESQ:
            self.proximo_token()  # consome '('
            expr = self.analisaExpA() # Vai começar a analisar uma nova expressão expA -> expM -> expPrim
            self.verificaProxToken(Pontuacao.PAREN_DIR) # consome ')'
            return expr

        # nenhum caso válido
        raise ParserError(
            f"Erro sintático na linha {tok.linha}, pos {tok.pos}: primária inválida, token {tok}"
        )

    # -------------------------
    # exp_m -> prim (('*'|'/') prim)*
    # -------------------------
    def analisaExpM(self) -> Exp:
        # inicia com uma primária
        esq = self.analisaPrim()

        # olhar sem consumir: get()
        tok = self.get()
        # enquanto houver * ou /
        while tok is not None and tok.tipo in (Operadores.MULTIPLIC, Operadores.DIVISAO):
            operador = tok.tipo
            # consome o operador
            self.proximo_token() # avança sem consumir
            # analisa o operando direito
            dir = self.analisaPrim()
            # construo nó binário (associatividade à esquerda)
            esq = OpBin(operador, esq, dir)
            tok = self.get()

        return esq

    # -------------------------
    # exp_a -> exp_m (('+'|'-') exp_m)*
    # -------------------------
    def analisaExpA(self) -> Exp:
        # inicia com um nível multiplicativo
        esq = self.analisaExpM()

        tok = self.get()
        # enquanto houver + ou -
        while tok is not None and tok.tipo in (Operadores.SOMA, Operadores.SUBTRACAO):
            operador = tok.tipo
            # consome o operador
            self.proximo_token()
            # analisa o próximo exp_m
            dir = self.analisaExpM()
            # construo nó binário (associatividade à esquerda)
            esq = OpBin(operador, esq, dir)
            tok = self.get()

        return esq
    
     # -------------------------
    # decl -> IDENT '=' exp ';'
    # programa -> decl* '=' exp EOF
    # -------------------------
    def parse_programa(self) -> Programa:
        declaracoes = []
        tok = self.get()
        # ler declarações enquanto houver identificador
        while tok is not None and tok.tipo == Identificador.IDENT:
            nome_tok = tok
            nome = nome_tok.lexema
            linha_ident = nome_tok.linha
            pos_ident = nome_tok.pos
            # consumir identificador
            self.proximo_token()
            # consumir '='
            self.verificaProxToken(Pontuacao.IGUAL)
            # analisar expressão do lado direito
            expr = self.analisaExpA()
            # exigir ';' no final da declaração
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            declaracoes.append(Decl(nome, expr, linha=linha_ident, pos=pos_ident))
            tok = self.get()

        # agora esperamos a expressão final que começa com '='
        tok = self.get()
        if tok is None or tok.tipo != Pontuacao.IGUAL:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(f"Erro sintático na linha {linha}, pos {pos}: esperado '=' iniciando expressão final, encontrado {tok}")
        # consumir '='
        self.proximo_token()
        exp_final = self.analisaExpA()
        # depois da expressão final deve vir EOF
        self.verificaProxToken(Pontuacao.EOF)
        return Programa(declaracoes, exp_final)

    def parse(self) -> Programa:
        return self.parse_programa()


if __name__ == '__main__':
    import sys
    from analisadorLexicoEV import AnalizadorLexico # Primeiro faz a análise léxica

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
    print("\nResultado da análise sintática:", ast)

    # impressão da expressão a partir da árvore 
    expr_str = ast.gerador()
    print("\nExpressão parseada: \n", expr_str)

    # Interpretação (resultado da expressão)
    resultado = ast.avaliador()
    print("\nResultado da avaliação:", resultado)
