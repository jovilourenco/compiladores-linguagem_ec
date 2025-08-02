"""
João Victor Lourenço da Silva (20220005997)

Sequência de execução e saída:
1. Análise Léxica
2. Análise Sintática
3. Impressão de tokens e AST
4. Geração de grafo da AST
"""

import os
import sys
from analisadorLexicoEC import AnalizadorLexico
from analisadorSintaticoEC import Parser, ParserError
from arvore import Exp
from criaGrafo import build_rich_tree
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

    # 4) Interpretação (avaliação)
    print("\n--- Resultado da avaliação ---")
    print(ast.avaliador())

    # 5) Geração do grafo da AST
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