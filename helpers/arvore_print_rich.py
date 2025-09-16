# João Victor Lourenço da Silva (20220005997)

from rich import print
from rich.tree import Tree
from .arvore import (
    Exp, Const, OpBin, Var, Decl, Programa,
    Stmt, Assign, IfStmt, WhileStmt, BlockStmt, ReturnStmt
)
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
    if op == Operadores.MENOR:
        return '<'
    if op == Operadores.MAIOR:
        return '>'
    if op == Operadores.IGUAL_IGUAL:
        return '=='
    return '?'

def build_rich_tree(node: Exp | Decl | Programa | Stmt, label: str = None) -> Tree:
    """
    Constrói uma Tree do rich a partir dos nós da AST.
    Suporta: Programa, Decl, Var, Const, OpBin, Assign, IfStmt, WhileStmt.
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
        # Comandos
        cmds_branch = Tree("Comandos")
        for c in node.comandos:
            # cada comando vira um sub-árvore
            cmds_branch.add(build_rich_tree(c))
        tree.add(cmds_branch)
        # Resultado / return
        res_branch = Tree("Resultado (return)")
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

    # Atribuição
    if isinstance(node, Assign):
        lbl = f"Atribuição: {node.nome} (linha={node.linha}, pos={node.pos})"
        t = Tree(lbl)
        t.add(build_rich_tree(node.expr))
        return t

    # If
    if isinstance(node, IfStmt):
        t = Tree("If")
        t.add(Tree("Condição").add(build_rich_tree(node.cond)))
        then_branch = Tree("Then")
        for s in node.then_stmts:
            then_branch.add(build_rich_tree(s))
        t.add(then_branch)
        if node.else_stmts is not None:
            else_branch = Tree("Else")
            for s in node.else_stmts:
                else_branch.add(build_rich_tree(s))
            t.add(else_branch)
        return t

    # While
    if isinstance(node, WhileStmt):
        t = Tree("While")
        t.add(Tree("Condição").add(build_rich_tree(node.cond)))
        body_branch = Tree("Corpo")
        for s in node.body:
            body_branch.add(build_rich_tree(s))
        t.add(body_branch)
        return t
    
    # Bloco
    if isinstance(node, BlockStmt):
        t = Tree("Bloco")
        for s in node.stmts:
            t.add(build_rich_tree(s))
        return t
    
    # Return
    if isinstance(node, ReturnStmt):
        t = Tree("Return")
        t.add(build_rich_tree(node.expr))
        return t

    # Fallback — representar genericamente
    return Tree(repr(node))