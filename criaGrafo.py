# João Victor Lourenço da Silva (20220005997)

from rich import print
from rich.tree import Tree
from arvore import Exp, Const, OpBin

def build_rich_tree(exp: Exp, label: str = None) -> Tree:
    if label is None:
        # raiz: usa o próprio símbolo ou valor
        if isinstance(exp, Const):
            label = str(exp.valor)
        else:
            label = {
                exp.operador.SOMA: "+",
                exp.operador.SUBTRACAO: "-",
                exp.operador.MULTIPLIC: "*",
                exp.operador.DIVISAO: "/",
            }[exp.operador]
    tree = Tree(label)
    if isinstance(exp, OpBin):
        tree.add(build_rich_tree(exp.opEsq))
        tree.add(build_rich_tree(exp.opDir))
    return tree