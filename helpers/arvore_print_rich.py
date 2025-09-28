# João Victor Lourenço da Silva (20220005997)
# helpers/arvore_print_rich.py
from rich import print
from rich.tree import Tree
from typing import Union

from .arvore import (
    Exp, Const, OpBin, Var, Decl, Programa,
    Stmt, Assign, IfStmt, WhileStmt, BlockStmt, ReturnStmt,
    FunDecl, Call
)
from helpers.token_tipos import Operadores

def _op_symbol(op: Operadores) -> str:
    """Retorna símbolo textual para o operador."""
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
    if op == Operadores.MENOR_IGUAL:
        return '<='
    if op == Operadores.MAIOR_IGUAL:
        return '>='
    if op == Operadores.DIFERENTE:
        return '!='
    if op == Operadores.RESTO:
        return '%'
    return '?'

Node = Union[Exp, Decl, Programa, Stmt, FunDecl]

def build_rich_tree(node: Node, label: str = None) -> Tree:
    """
    Constrói uma Tree do rich a partir dos nós da AST.
    Suporta: Programa, Decl, Var, Const, OpBin, Assign, IfStmt, WhileStmt,
             BlockStmt, ReturnStmt, FunDecl, Call.
    """
    # Programa (raiz)
    if isinstance(node, Programa):
        tree = Tree("Programa")

        # Variáveis globais (var_decls)
        vars_branch = Tree("Var_decls (globais)")
        for d in node.var_decls:
            d_label = f"Decl: {d.nome} (linha={d.linha}, pos={d.pos})"
            d_tree = Tree(d_label)
            d_tree.add(build_rich_tree(d.expr))
            vars_branch.add(d_tree)
        tree.add(vars_branch)

        # Funções
        funs_branch = Tree("Fun_decls")
        for f in node.fun_decls:
            fn_label = f"Fun: {f.nome}({', '.join(f.params)}) (linha={f.linha}, pos={f.pos})"
            fn_tree = Tree(fn_label)
            # parâmetros
            params_tree = Tree("Params")
            if f.params:
                for p in f.params:
                    params_tree.add(Tree(f"{p}"))
            else:
                params_tree.add(Tree("<nenhum>"))
            fn_tree.add(params_tree)
            # declarações locais
            locals_tree = Tree("Local_decls")
            for d in f.local_decls:
                ld = Tree(f"Decl: {d.nome} (linha={d.linha}, pos={d.pos})")
                ld.add(build_rich_tree(d.expr))
                locals_tree.add(ld)
            fn_tree.add(locals_tree)
            # comandos da função
            cmds_tree = Tree("Comandos")
            for c in f.comandos:
                cmds_tree.add(build_rich_tree(c))
            fn_tree.add(cmds_tree)
            # resultado/return da função
            res_tree = Tree("Resultado (return)")
            res_tree.add(build_rich_tree(f.resultado))
            fn_tree.add(res_tree)

            funs_branch.add(fn_tree)
        tree.add(funs_branch)

        # Comandos do main
        cmds_branch = Tree("Comandos (main)")
        for c in node.comandos:
            cmds_branch.add(build_rich_tree(c))
        tree.add(cmds_branch)

        # Resultado do main
        res_branch = Tree("Resultado (return main)")
        res_branch.add(build_rich_tree(node.resultado))
        tree.add(res_branch)

        return tree

    # Decl isolada
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

    # Chamada de função
    if isinstance(node, Call):
        lbl = f"Call: {node.nome}({len(node.args)} args) (linha={node.linha}, pos={node.pos})"
        t = Tree(lbl)
        if node.args:
            for a in node.args:
                t.add(build_rich_tree(a))
        else:
            t.add(Tree("<sem-args>"))
        return t

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
        cond = Tree("Condição")
        cond.add(build_rich_tree(node.cond))
        t.add(cond)
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
        cond = Tree("Condição")
        cond.add(build_rich_tree(node.cond))
        t.add(cond)
        body_branch = Tree("Corpo")
        for s in node.body:
            body_branch.add(build_rich_tree(s))
        t.add(body_branch)
        return t

    # Bloco composto
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
