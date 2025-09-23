# João Victor Lourenço da Silva (20220005997)

from helpers.token_tipos import Numero, Operadores, Pontuacao, Identificador, Error, PalavraReservada
from helpers.token import Token

class AnalizadorLexico:
    def __init__(self, texto: str):
        self.texto = texto
        self.i = 0 # posicao atual
        self.n = len(texto) # tamanho da expressao
        self.linha = 1

    # get pega o que está na posição atual. Se a posição atual for maior que o tam. máximo do arquivo, insere \0
    def get(self) -> str:
        return self.texto[self.i] if self.i < self.n else '\0'

    # incrementa o 'ponteiro' leitor do arquivo.
    def proximo_token(self):
        if self.i < self.n and self.texto[self.i] == '\n':
            self.linha += 1
        self.i += 1

    def verificaProxToken(self) -> str:
        return self.texto[self.i + 1] if (self.i + 1) < self.n else '\0'

    def verificaNumero(self, inicio: int) -> Token: # Verificar se é um número mesmo
        lex = ''
        while self.get().isdigit():
            lex += self.get()
            self.proximo_token()
        if self.get().isalnum(): # Agora, se vier alguma letra depois dos dígitos já vai dar erro
            while self.get().isalnum():
                lex += self.get()
                self.proximo_token()
            return Token(Error.LEX_ERROR, lex, inicio, self.linha)
        return Token(Numero.NUMERO, lex, inicio, self.linha)
    
    def verificaIdentificador(self, inicio: int) -> Token: 
        lex = ''
        while self.get().isalnum():  # letra ou dígito (mas quando entra na função, já é letra).
            lex += self.get()
            self.proximo_token()
        
        # Agora, tem que verificar as palavras chave: if, else, while, return, fun, var, main.
        lower = lex.lower()
        if lower == 'if':
            return Token(PalavraReservada.IF, lex, inicio, self.linha)
        if lower == 'else':
            return Token(PalavraReservada.ELSE, lex, inicio, self.linha)
        if lower == 'while':
            return Token(PalavraReservada.WHILE, lex, inicio, self.linha)
        if lower == 'return':
            return Token(PalavraReservada.RETURN, lex, inicio, self.linha)
        if lower == 'fun':
            return Token(PalavraReservada.FUN, lex, inicio, self.linha)
        if lower == 'var':
            return Token(PalavraReservada.VAR, lex, inicio, self.linha)
        if lower == 'main':
            return Token(PalavraReservada.MAIN, lex, inicio, self.linha)

        return Token(Identificador.IDENT, lex, inicio, self.linha)

    def classificador(self) -> Token:
        # pula espaços em branco
        while self.get().isspace():
            self.proximo_token()

        inicio = self.i # define a posição inicial do token
        carac = self.get() 

        # finaliza o processamento
        if carac == '\0':
            return None

        # se for dígito, iterar até formar o digito
        if carac.isdigit():
            return self.verificaNumero(inicio)
        
        # se for letra, iterar até formar identificador
        if carac.isalpha():
            return self.verificaIdentificador(inicio)

        # Verifica se é ==
        if carac == '=' and self.verificaProxToken() == '=':
            self.proximo_token()
            self.proximo_token()
            return Token(Operadores.IGUAL_IGUAL, '==', inicio, self.linha)

        self.proximo_token() # desloca o ponteiro

        # operadores
        if carac == '+':
            return Token(Operadores.SOMA, carac, inicio, self.linha)
        if carac == '-':
            return Token(Operadores.SUBTRACAO, carac, inicio, self.linha)
        if carac == '*':
            return Token(Operadores.MULTIPLIC, carac, inicio, self.linha)
        if carac == '/':
            return Token(Operadores.DIVISAO, carac, inicio, self.linha)

        # Verifica se é < ou >
        if carac == '<':
            return Token(Operadores.MENOR, carac, inicio, self.linha)
        if carac == '>':
            return Token(Operadores.MAIOR, carac, inicio, self.linha)

        # pontuação
        # pontuação
        if carac == '(':
            return Token(Pontuacao.PAREN_ESQ, carac, inicio, self.linha)
        if carac == ')':
            return Token(Pontuacao.PAREN_DIR, carac, inicio, self.linha)
        if carac == '{':
            return Token(Pontuacao.CHAVE_ESQ, carac, inicio, self.linha)
        if carac == '}':
            return Token(Pontuacao.CHAVE_DIR, carac, inicio, self.linha)
        if carac == '=':  # operador de atribuição / início do resultado
            return Token(Pontuacao.IGUAL, carac, inicio, self.linha)
        if carac == ';':
            return Token(Pontuacao.PONTO_VIRGULA, carac, inicio, self.linha)
        if carac == ',':
            return Token(Pontuacao.VIRGULA, carac, inicio, self.linha)

        # erro léxico
        return Token(Error.LEX_ERROR, carac, inicio, self.linha)

        # se não for nenhuma das validações acima: caractere inválido = erro léxico
        # raise SyntaxError(f"Erro léxico na linha {self.linha}, posição {inicio}: caractere inválido '{carac}'")

    # Cria a lista de tokens para exibir (Ele quem inicia toda tokenização)
    def tokenizador(self) -> list[Token]:
        tokens = []
        while True:
            tok = self.classificador()
            if tok is None:
                tokens.append(Token(Pontuacao.EOF, '', self.i, self.linha)) # Adiciona EOF no final - Para o analisador léxico, por enquanto.
                break  # fim implícito, não gera EOF
            tokens.append(tok)
        return tokens


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Uso: python analisadorLexicoEC.py <arquivo.txt>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        entrada = f.read()

    lexer = AnalizadorLexico(entrada)
    for token in lexer.tokenizador():
        print(token)