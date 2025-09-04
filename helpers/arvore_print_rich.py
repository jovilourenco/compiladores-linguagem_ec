# João Victor Lourenço da Silva (20220005997)
from rich import print
from rich.tree import Tree
from .arvore import Exp, Const, OpBin, Var, Decl, Programa
from helpers.token_tipos import Operadores

def _op_symbol(op: Operadores) -> str:
    if op == Operadores.SOMA:
        return '+'
    if op == Operadores.SUBTRACAO:
        return '-'
    if op == Operadores.MULTIPLIC:
        return '*'
    if op == Operadores.DIVISAO:
        return '/'
    return '?'

def build_rich_tree(node: Exp | Decl | Programa, label: str = None) -> Tree:
    """
    Constrói uma Tree do rich a partir dos nós da AST.
    Suporta: Programa, Decl, Var, Const, OpBin.
    """
    # Programa (raiz)
    if isinstance(node, Programa):
        tree = Tree("Programa")
        # Declarações
        decls_branch = Tree("Declarações")
        for d in node.declaracoes:
            d_label = f"Decl: {d.nome} (linha={d.linha}, pos={d.pos})"
            d_tree = Tree(d_label)
            d_tree.add(build_rich_tree(d.expr))
            decls_branch.add(d_tree)
        tree.add(decls_branch)
        # Resultado
        res_branch = Tree("Resultado")
        res_branch.add(build_rich_tree(node.resultado))
        tree.add(res_branch)
        return tree

    # Decl isolada (caso alguém chame com Decl diretamente)
    if isinstance(node, Decl):
        tree = Tree(f"Decl: {node.nome} (linha={node.linha}, pos={node.pos})")
        tree.add(build_rich_tree(node.expr))
        return tree

    # Constante
    if isinstance(node, Const):
        return Tree(str(node.valor))

    # Variável
    if isinstance(node, Var):
        lbl = f"Var: {node.nome} (linha={node.linha}, pos={node.pos})"
        return Tree(lbl)

    # Operação binária
    if isinstance(node, OpBin):
        sym = _op_symbol(node.operador)
        tree = Tree(sym)
        tree.add(build_rich_tree(node.opEsq))
        tree.add(build_rich_tree(node.opDir))
        return tree

    # Fallback — representar genericamente
    return Tree(repr(node))
