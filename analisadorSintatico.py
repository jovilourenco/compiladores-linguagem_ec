# João Victor Lourenço da Silva (20220005997)

from typing import List, Optional

from helpers.token import Token
from helpers.token_tipos import Numero, Identificador, Operadores, Pontuacao, Error, PalavraReservada
from helpers.arvore import Exp, Const, OpBin, Var, Decl, Programa, Stmt, Assign, IfStmt, WhileStmt, BlockStmt, ReturnStmt, FunDecl, Call

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

            prox = self.tokens[self.pos + 1] if (self.pos + 1) < len(self.tokens) else None
            if prox is not None and prox.tipo == Pontuacao.PAREN_ESQ:
                self.proximo_token() #consome o identificador
                self.verificaProxToken(Pontuacao.PAREN_ESQ) #consome o (
                args = [] #argumentos
                tok2 = self.get()
                if tok2 is not None and tok2.tipo != Pontuacao.PAREN_DIR:
                    #se entrou aqui é pq tem pelo menos 1 argumento
                    args.append(self.analisaExpC())
                    tok2 = self.get()
                    while tok2 is not None and tok2.tipo == Pontuacao.VIRGULA:
                        #Vai consumindo o restante dos argumentos e adicionando em args
                        self.proximo_token()
                        args.append(self.analisaExpC())
                        tok2 = self.get()
                self.verificaProxToken(Pontuacao.PAREN_DIR)
                return Call(nome,args,linha=linha,pos=pos)
            else:
                self.proximo_token()
                return Var(nome,linha=linha,pos=pos)

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
        while tok is not None and tok.tipo in (Operadores.MULTIPLIC, Operadores.DIVISAO, Operadores.RESTO):
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
        while tok is not None and tok.tipo in (Operadores.MENOR, Operadores.MAIOR, Operadores.IGUAL_IGUAL,
            Operadores.MENOR_IGUAL, Operadores.MAIOR_IGUAL, Operadores.DIFERENTE):
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
            
            ntok = self.get()
            # caso normal: '='
            if ntok is not None and ntok.tipo == Pontuacao.IGUAL:
                self.proximo_token()
                expr = self.analisaExpC()
                self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
                return Assign(nome, expr, linha=linha, pos=pos)

            # atribuições compostas: '+=', '-=', '*=', '/='
            if ntok is not None and ntok.tipo in (Operadores.ADDEQ, Operadores.SUBEQ, Operadores.MULEQ, Operadores.DIVEQ):
                op_tok = ntok.tipo
                self.proximo_token()  # consome operador composto
                rhs = self.analisaExpC()
                self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
                # verifica qual o token composto para operador binário correspondente
                if op_tok == Operadores.ADDEQ:
                    binop = Operadores.SOMA
                elif op_tok == Operadores.SUBEQ:
                    binop = Operadores.SUBTRACAO
                elif op_tok == Operadores.MULEQ:
                    binop = Operadores.MULTIPLIC
                elif op_tok == Operadores.DIVEQ:
                    binop = Operadores.DIVISAO
                else:
                    raise ParserError("Operador composto desconhecido")
                from helpers.arvore import Var, OpBin 
                return Assign(nome, OpBin(binop, Var(nome, linha=linha, pos=pos), rhs), linha=linha, pos=pos)

            # incremento/decremento postfix: '++' / '--'
            if ntok is not None and ntok.tipo in (Operadores.INC, Operadores.DEC):
                inc_tok = ntok.tipo
                self.proximo_token()  # consome ++/--
                self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
                from helpers.arvore import Var, Const, OpBin
                if inc_tok == Operadores.INC:
                    return Assign(nome, OpBin(Operadores.SOMA, Var(nome, linha=linha, pos=pos), Const(1)), linha=linha, pos=pos)
                else:
                    return Assign(nome, OpBin(Operadores.SUBTRACAO, Var(nome, linha=linha, pos=pos), Const(1)), linha=linha, pos=pos)
                
            # se não foi nenhum caso acima, é erro sintático
            pos_err = ntok.pos if ntok else self.pos
            linha_err = ntok.linha if ntok else '?'
            raise ParserError(f"Erro na linha {linha_err}, pos {pos_err}: esperado operador de atribuição ou '++'/'--', encontrado {ntok}")
        
        if tok.tipo == PalavraReservada.RETURN:
            # consumir 'return'
            self.proximo_token()
            expr = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            return ReturnStmt(expr, linha=tok.linha, pos=tok.pos)

        # caso inválido
        raise ParserError(f"Erro na linha {tok.linha}, pos {tok.pos}: comando inválido, token {tok}")

    #vardecl ::= 'var' <ident> '=' <exp> ';'
    def parse_var_decl(self) -> Decl:
        tok = self.get()
        if tok is None or tok.tipo != PalavraReservada.VAR:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(f"Erro na linha {linha}, pos {pos}: esperado 'var' iniciando declaração de variável, encontrado {tok}")
        #Consumir o 'var'
        self.proximo_token()
        nome_tok = self.verificaProxToken(Identificador.IDENT)
        nome = nome_tok.lexema
        linha_ident = nome_tok.linha
        pos_ident = nome_tok.pos
        #Consumir a atribuição '='
        self.verificaProxToken(Pontuacao.IGUAL)
        expr = self.analisaExpC()
        self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
        return Decl(nome,expr,linha=linha_ident,pos=pos_ident)

    # fundecl ::= 'fun' <ident> '(' <args>? ')' '{' <vardecl>* <cmd>* 'return' <exp> ';' '}'
    def parse_fun_decl(self) -> FunDecl:
        tok = self.get()
        if tok is None or tok.tipo != PalavraReservada.FUN:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(f"Erro na linha {linha}, pos {pos}: esperado 'fun' iniciando declaração de função, encontrado {tok}")
        self.proximo_token() # Consumir o fun
        nome_tok = self.verificaProxToken(Identificador.IDENT)
        nome = nome_tok.lexema
        linha_ident = nome_tok.linha
        pos_ident = nome_tok.pos
        # Parametros formais
        self.verificaProxToken(Pontuacao.PAREN_ESQ)
        params: List[str] = []
        tok2 = self.get()
        if tok2 is not None and tok2.tipo != Pontuacao.PAREN_DIR:
            # pelo menos um parâmetro
            p_tok = self.verificaProxToken(Identificador.IDENT)
            params.append(p_tok.lexema)
            tok2 = self.get()
            while tok2 is not None and tok2.tipo == Pontuacao.VIRGULA:
                self.proximo_token()  # consome ','
                p_tok = self.verificaProxToken(Identificador.IDENT)
                params.append(p_tok.lexema)
                tok2 = self.get()
        self.verificaProxToken(Pontuacao.PAREN_DIR)

        # corpo da função
        self.verificaProxToken(Pontuacao.CHAVE_ESQ)
        # primeiro parse de declarações locais 'var'*
        local_decls: List[Decl] = []
        while True:
            ntok = self.get()
            if ntok is None:
                raise ParserError("Fim inesperado dentro de função, esperado '}'")
            if ntok.tipo == PalavraReservada.VAR:
                d = self.parse_var_decl()
                local_decls.append(d)
                continue
            break

        # comandos até return
        comandos = self.parse_commands_until_return()

        # agora 'return' obrigatório dentro da função
        self.verificaProxToken(PalavraReservada.RETURN)
        resultado = self.analisaExpC()
        self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
        # fechar '}'
        self.verificaProxToken(Pontuacao.CHAVE_DIR)

        return FunDecl(nome, params, local_decls, comandos, resultado, linha=linha_ident, pos=pos_ident)

    # Novo parser para a linguagem EV
    def parse_programa(self) -> Programa:
        var_decls: List[Decl] = []
        fun_decls: List[FunDecl] = []

        tok = self.get()
        # ler declarações (var / fun) em qualquer ordem
        while tok is not None and (tok.tipo == PalavraReservada.VAR or tok.tipo == PalavraReservada.FUN):
            if tok.tipo == PalavraReservada.VAR:
                d = self.parse_var_decl()
                var_decls.append(d)
            else:
                # FUN
                f = self.parse_fun_decl()
                fun_decls.append(f)
            tok = self.get()

        # agora esperamos 'main'
        tok = self.get()
        if tok is None or tok.tipo != PalavraReservada.MAIN:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(f"Erro na linha {linha}, pos {pos}: esperado 'main' iniciando bloco principal, encontrado {tok}")
        # consome 'main'
        self.proximo_token()
        self.verificaProxToken(Pontuacao.CHAVE_ESQ)

        # Observação: main NÃO pode conter declarações 'var' locais -> se houver, erro de sintaxe.
        # Ler comandos até return ou '}' (mesmo comportamento anterior)
        comandos = []
        while True:
            ntok = self.get()
            if ntok is None:
                raise ParserError("Fim inesperado dentro do main: esperado 'return' ou '}'")
            if ntok.tipo == PalavraReservada.RETURN:
                break
            if ntok.tipo == Pontuacao.CHAVE_DIR:
                break
            # detecta 'var' dentro de main -> erro (religioso a sua restrição)
            if ntok.tipo == PalavraReservada.VAR:
                raise ParserError(f"Erro na linha {ntok.linha}, pos {ntok.pos}: declaração 'var' não permitida dentro de main")
            comandos.append(self.analisaComando())

        # se houver 'return' processa retorno, senão considera resultado Const(0)
        tok = self.get()
        if tok is not None and tok.tipo == PalavraReservada.RETURN:
            self.proximo_token()
            resultado = self.analisaExpC()
            self.verificaProxToken(Pontuacao.PONTO_VIRGULA)
            self.verificaProxToken(Pontuacao.CHAVE_DIR)
            self.verificaProxToken(Pontuacao.EOF)
            return Programa(var_decls, fun_decls, comandos, resultado)
        elif tok is not None and tok.tipo == Pontuacao.CHAVE_DIR:
            # main sem return - fecha e EOF
            self.proximo_token()
            self.verificaProxToken(Pontuacao.EOF)
            resultado = Const(0)
            return Programa(var_decls, fun_decls, comandos, resultado)
        else:
            pos = tok.pos if tok else self.pos
            linha = tok.linha if tok else '?'
            raise ParserError(f"Erro na linha {linha}, pos {pos}: esperado 'return' ou '}}' fechando main, encontrado {tok}")

    def parse(self) -> Programa:
        return self.parse_programa()


if __name__ == '__main__':
    import sys
    from analisadorLexico import AnalizadorLexico # Primeiro faz a análise léxica

    if len(sys.argv) != 2:
        print("Uso: python analisadorSintatico.py <arquivo.txt>")
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
    print("\nPrograma gerado: \n", expr_str)

    # Interpretação (resultado da expressão)
    try:
        resultado = ast.avaliador()
    except Exception as e:
        print("Erro em tempo de execução/semântico:", e)
        sys.exit(1)
    print("\nResultado da avaliação:", resultado)