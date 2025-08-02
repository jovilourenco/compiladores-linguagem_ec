# João Victor Lourenço da Silva (20220005997)

from token_tipos import Numero, Operadores, Pontuacao, Error
from lex_token import Token

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

    def verificaNumero(self, inicio: int) -> Token: # Verificar se é um número mesmo
        lex = ''
        while self.get().isdigit():
            lex += self.get()
            self.proximo_token()
        return Token(Numero.NUMERO, lex, inicio)

    def classificador(self) -> Token:
        # pula espaços em branco
        while self.get().isspace():
            self.proximo_token()

        inicio = self.i # define a posição inicial do token
        carac = self.get() 

        # finaliza o processamento
        if carac == '\0':
            return None

        # se for dígito, iterar até formar o token completo (dígito)
        if carac.isdigit():
            return self.verificaNumero(inicio)

        self.proximo_token()

        # operadores
        if carac == '+':
            return Token(Operadores.SOMA, carac, inicio)
        if carac == '-':
            return Token(Operadores.SUBTRACAO, carac, inicio)
        if carac == '*':
            return Token(Operadores.MULTIPLIC, carac, inicio)
        if carac == '/':
            return Token(Operadores.DIVISAO, carac, inicio)

        # pontuação
        if carac == '(':
            return Token(Pontuacao.PAREN_ESQ, carac, inicio)
        if carac == ')':
            return Token(Pontuacao.PAREN_DIR, carac, inicio)

        # erro léxico
        return Token(Error.LEX_ERROR, carac, inicio)

        # se não for nenhuma das validações acima: caractere inválido = erro léxico
        # raise SyntaxError(f"Erro léxico na linha {self.linha}, posição {inicio}: caractere inválido '{carac}'")

    # Cria a lista de tokens para exibir (Ele quem inicia toda tokenização)
    def tokenizador(self) -> list[Token]:
        tokens = []
        while True:
            tok = self.classificador()
            if tok is None:
                tokens.append(Token(Pontuacao.EOF, '', self.i)) # Adiciona EOF no final - Para o analisador léxico, por enquanto.
                break  # fim implícito, não gera EOF
            tokens.append(tok)
        return tokens


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Uso: python -m lexer.lexer <arquivo.ec1>")
        sys.exit(1)

    with open(sys.argv[1], 'r') as f:
        entrada = f.read()

    lexer = AnalizadorLexico(entrada)
    for token in lexer.tokenizador():
        print(token)