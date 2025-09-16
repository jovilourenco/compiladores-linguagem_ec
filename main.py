"""
João Victor Lourenço da Silva (20220005997)

Sequência de execução e saída:
1. Análise Léxica
2. Análise Sintática
3. Impressão de tokens e AST
4. Print de árvore com rich
"""

import os
import sys
from analisadorLexico import AnalizadorLexico
from analisadorSintatico import Parser, ParserError
from helpers.arvore import Exp
from helpers.arvore_print_rich import build_rich_tree
from rich import print as rprint
from gerador import gera_codigo


def main():
    if len(sys.argv) != 2:
        print("Uso: python main.py <arquivo.txt>")
        sys.exit(1)

    # 1) Análise Léxica
    arquivo = sys.argv[1]
    with open(arquivo, 'r') as f:
        texto = f.read()
    lexer = AnalizadorLexico(texto)
    tokens = lexer.tokenizador()

    print("\n--- Tokens ---")
    for tok in tokens:
        print(tok)

    # 2) Análise Sintática
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except ParserError as e:
        print("Erro sintático:", e)
        sys.exit(1)

    print("\n--- Análise sintática ---")
    print(ast)

    # 3) Impressão da expressão a partir da AST
    print("\n--- Expressão gerada ---")
    print(ast.gerador())

    # 3.5) Verificação semântica (antes de executar/avaliar)
    try:
        # chama o método de verificação estática que percorre declarações, comandos e retorno
        ast.verifica_semantica()
    except NameError as e:
        print("Erro semântico:", e)
        sys.exit(1)

    # 4) Interpretação (avaliação)
    print("\n--- Resultado da avaliação ---")
    try:
        resultado = ast.avaliador()
        print(resultado)
    except Exception as e:
        print("\nErro durante avaliação/semântica:", e)
        sys.exit(1)

    # 5) Geração da AST
    rich_tree = build_rich_tree(ast)
    print("\n--- Printa árvore com Rich ---")
    rprint(rich_tree)

    print("\n--- Gerando código Assembly ---")
    os.makedirs("assemblys", exist_ok=True)
    asm = gera_codigo(ast)
    out_path = os.path.join("assemblys", "saida.s")
    with open(out_path, 'w') as f:
        f.write(asm)
    print(f"Assembly gerado em: {out_path}")


if __name__ == '__main__':
    main()
