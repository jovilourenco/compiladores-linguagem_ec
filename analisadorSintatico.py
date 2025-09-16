# João Victor Lourenço da Silva (20220005997)

from typing import List, Optional

from helpers.token import Token
from helpers.token_tipos import Numero, Identificador, Operadores, Pontuacao, Error, PalavraReservada
from helpers.arvore import Exp, Const, OpBin, Var, Decl, Programa, Stmt, Assign, IfStmt, WhileStmt, BlockStmt, ReturnStmt

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
                f"Erro na linha {linha}, pos {pos}: esperado {tipo_esperado}, encontrado {tok}"
            )
        self.proximo_token()
        return tok

    # prim -> número | '(' exp_a ')'
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
            f"Erro na linha {tok.linha}, pos {tok.pos}: primária inválida, token {tok}"
        )

    
    # exp_m -> prim (('*'|'/') prim)*
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

    # exp_a -> exp_m (('+'|'-') exp_m)*
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
    
    # Como temos um novo "nível" de precedência (comparações) criei a função para os comparadores.
    def analisaExpC(self) -> Exp:
        esq = self.analisaExpA()
        tok = self.get()
        while tok is not None and tok.tipo in (Operadores.MENOR, Operadores.MAIOR, Operadores.IGUAL_IGUAL):
            operador = tok.tipo
            self.proximo_token()
            dir = self.analisaExpA()
            esq = OpBin(operador, esq, dir)
            tok = self.get()
        return esq
    
    # Comandos até '}' sem consumir }
    def parse_block(self) -> List['Stmt']:
        stmts: List[Stmt] = []
        while True:
            tok = self.get()
            if tok is None:
                raise ParserError("Fim inesperado dentro de bloco, esperado '}'")
            if tok.tipo == Pontuacao.CHAVE_DIR:
                break
            stmts.append(self.analisaComando())
        return stmts
    
    #Comandos até o 'return' sem consumir o return
    def parse_commands_until_return(self) -> List['Stmt']:
        stmts: List[Stmt] = []
        while True:
            tok = self.get()
            if tok is None:
                raise ParserError("Fim inesperado dentro do bloco principal: esperado 'return' ou '}'")
            # se encontramos 'return' no nível superior, interrompemos (não consumimos aqui)
            if tok.tipo == PalavraReservada.RETURN:
                break
            # se encontramos '}' significa fim do bloco principal sem return no nível superior -> interrompe
            if tok.tipo == Pontuacao.CHAVE_DIR:
                break
            stmts.append(self.analisaComando())
        return stmts
    
    # Função que verifica os comandos e suas respectivas estruturas.
    def analisaComando(self) -> 'Stmt':
        tok = self.get()
        if tok is None:
            raise ParserError("Fim inesperado ao analisar comando")

        # if
        if tok.tipo == PalavraReservada.IF:
            self.proximo_token()
            self.verificaProxToken(Pontuacao.PAREN_ESQ)
            cond = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PAREN_DIR)
            self.verificaProxToken(Pontuacao.CHAVE_ESQ)
            then_stmts = self.parse_block()
            self.verificaProxToken(Pontuacao.CHAVE_DIR)
            else_stmts = None
            ntok = self.get()
            if ntok is not None and ntok.tipo == PalavraReservada.ELSE:
                self.proximo_token()
                self.verificaProxToken(Pontuacao.CHAVE_ESQ)
                else_stmts = self.parse_block()
                self.verificaProxToken(Pontuacao.CHAVE_DIR)
            return IfStmt(cond, then_stmts, else_stmts)

        # while
        if tok.tipo == PalavraReservada.WHILE:
            self.proximo_token()
            self.verificaProxToken(Pontuacao.PAREN_ESQ)
            cond = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PAREN_DIR)
            self.verificaProxToken(Pontuacao.CHAVE_ESQ)
            body = self.parse_block()
            self.verificaProxToken(Pontuacao.CHAVE_DIR)
            return WhileStmt(cond, body)

        # bloco composto (um bloco isolado também é um comando válido)
        if tok.tipo == Pontuacao.CHAVE_ESQ:
            # consumir '{', ler blocos internos com parse_block, consumir '}'
            self.proximo_token()  # consome '{'
            inner_stmts = self.parse_block()
            self.verificaProxToken(Pontuacao.CHAVE_DIR)
            return BlockStmt(inner_stmts)

        # atribuição (inicia com identificador)
        if tok.tipo == Identificador.IDENT:
            nome = tok.lexema
            linha = tok.linha
            pos = tok.pos
            self.proximo_token()
            self.verificaProxToken(Pontuacao.IGUAL)
            expr = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            return Assign(nome, expr, linha=linha, pos=pos)
        
        if tok.tipo == PalavraReservada.RETURN:
            # consumir 'return'
            self.proximo_token()
            expr = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            return ReturnStmt(expr, linha=tok.linha, pos=tok.pos)

        # caso inválido
        raise ParserError(f"Erro na linha {tok.linha}, pos {tok.pos}: comando inválido, token {tok}")

    # Novo parser para a linguagem EV
    def parse_programa(self) -> Programa:
        declaracoes = [] # Declarações é o array de Decl(nome,expr,linha,pos) das declarações.
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
            # analisar os comandos, primeiro, agora.
            expr = self.analisaExpC()
            # exigir ';' no final da declaração
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            declaracoes.append(Decl(nome, expr, linha=linha_ident, pos=pos_ident))
            tok = self.get()

        # agora esperamos a chave { para iniciar o main
        tok = self.get()
        if tok is None or tok.tipo != Pontuacao.CHAVE_ESQ:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            
            raise ParserError(f"Erro na linha {linha}, pos {pos}: esperado '{{' iniciando bloco principal, encontrado {tok}")
        # consumir '{'
        self.proximo_token()
        
        # ler comandos até 'return'
        comandos = self.parse_commands_until_return()

        # agora verificar o que vem a seguir: se for 'return' processamos o retorno (caso clássico),
        # se for '}' então o bloco principal terminou sem um return no nível superior.
        tok = self.get()
        if tok is not None and tok.tipo == PalavraReservada.RETURN:
            # 'return' e expressão de retorno (caso clássico)
            self.proximo_token()  # consome 'return'
            resultado = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            # consumir '}' final do bloco principal
            self.verificaProxToken(Pontuacao.CHAVE_DIR)
            # deve vir EOF em seguida
            self.verificaProxToken(Pontuacao.EOF)
            return Programa(declaracoes, comandos, resultado)
        elif tok is not None and tok.tipo == Pontuacao.CHAVE_DIR:
            # caso sem 'return' no nível superior: consumimos '}' e EOF e usamos Const(0) como resultado padrão.
            self.proximo_token()  # consome '}'
            self.verificaProxToken(Pontuacao.EOF)
            resultado = Const(0)
            return Programa(declaracoes, comandos, resultado)
        else:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(f"Erro na linha {linha}, pos {pos}: esperado 'return' ou '}}' fechando bloco principal, encontrado {tok}")

    def parse(self) -> Programa:
        return self.parse_programa()


if __name__ == '__main__':
    import sys
    from analisadorLexico import AnalizadorLexico # Primeiro faz a análise léxica

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
