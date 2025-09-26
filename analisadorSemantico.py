# analisadorSemantico.py
from typing import Dict, Any, Set
from helpers.arvore import (
    Programa, Const, Var, OpBin, Decl, Stmt, Assign,
    IfStmt, WhileStmt, BlockStmt, ReturnStmt, Call, FunDecl
)

def build_symbol_table_and_offsets(program: Programa) -> Dict[str, Any]:
    """
    Constrói tabela global e preenche offsets em cada função AST.
    Além disso realiza checagens semânticas:
      - permite recursão direta (registrando assinatura antes de checar o corpo)
      - verifica chamadas de funções (existe + aridade)
      - verifica uso de variáveis (procura local -> global)
      - verifica LHS de atribuições (já declarado)
      - verifica a restrição 'main não pode ter variáveis locais' (se aplicável)
    Retorna symtab para uso posterior pelo gerador.
    """
    symtab: Dict[str, Dict[str, Any]] = {}

    # ---------- PASSO A: registrar globais e assinaturas de funções (permite recursão direta) ----------
    # registrar variáveis globais (declarações do topo) -> AST usa var_decls
    for d in getattr(program, 'var_decls', []):
        name = d.nome
        if name in symtab:
            raise NameError(f"Redeclaração global: {name}")
        # marca como variável global
        symtab[name] = {'kind': 'var', 'name': name}

    # localizar declarações de funções (program.fun_decls)
    fun_decls = getattr(program, 'fun_decls', [])
    # 1ª passada: registrar apenas a assinatura (nome e número de parâmetros)
    for f in fun_decls:
        if f.nome in symtab:
            raise NameError(f"Nome já usado (variável ou função) em nível global: {f.nome}")
        params = getattr(f, 'params', [])  # lista de nomes formais (ex.: ['x','y'])
        symtab[f.nome] = {
            'kind': 'fun',
            'name': f.nome,
            'num_params': len(params),
            'params': list(params),
            # placeholders: serão preenchidos na segunda passada
            'param_offsets': {},
            'local_offsets': {},
            'frame_size': 0
        }

    # ---------- PASSO B: calcular offsets e verificar corpos ----------
    def _compute_offsets_for_function(f) -> None:
        params = getattr(f, 'params', [])
        locals_names = [d.nome for d in getattr(f, 'local_decls', [])]

        # param offsets: first param at rbp+16, second rbp+24, ...
        param_offsets = {}
        for i, pname in enumerate(params):
            param_offsets[pname] = 16 + 8 * i

        # local offsets: start at -8, -16, ...
        local_offsets = {}
        for i, lname in enumerate(locals_names, start=1):
            local_offsets[lname] = -8 * i

        frame_size = 8 * len(locals_names)  # alinhado a 8

        setattr(f, 'param_offsets', param_offsets)
        setattr(f, 'local_offsets', local_offsets)
        setattr(f, 'frame_size', frame_size)
        setattr(f, 'num_params', len(params))

        # atualiza symtab
        symtab[f.nome]['param_offsets'] = param_offsets
        symtab[f.nome]['local_offsets'] = local_offsets
        symtab[f.nome]['frame_size'] = frame_size
        symtab[f.nome]['num_params'] = len(params)

    # calcula offsets para todas as funções (antes de checar corpos)
    for f in fun_decls:
        _compute_offsets_for_function(f)

    # Funções auxiliares de checagem de expressões e comandos
    def check_expr(e, local_names: Set[str], available_funs: Set[str]):
        """Verifica recursivamente uma expressão e levanta NameError em violação."""
        # Const
        if isinstance(e, Const):
            return
        # Var (referência)
        if isinstance(e, Var):
            if e.nome not in local_names and e.nome not in symtab:
                ln = getattr(e, 'linha', '?')
                ps = getattr(e, 'pos', '?')
                raise NameError(f"Erro semântico: variável '{e.nome}' não declarada (linha {ln}, pos {ps})")
            return
        # Binary op
        if isinstance(e, OpBin):
            check_expr(e.opEsq, local_names, available_funs)
            check_expr(e.opDir, local_names, available_funs)
            return

        # Call node (sua AST tem Call)
        if isinstance(e, Call) or (hasattr(e, 'nome') and hasattr(e, 'args')):
            fname = e.nome
            args = e.args
            # função deve estar registrada globalmente como função
            if fname not in symtab or symtab[fname]['kind'] != 'fun':
                ln = getattr(e, 'linha', '?')
                ps = getattr(e, 'pos', '?')
                raise NameError(f"Erro semântico: chamada para função não declarada '{fname}' (linha {ln}, pos {ps})")
            expected = symtab[fname]['num_params']
            actual = len(args)
            if expected != actual:
                ln = getattr(e, 'linha', '?')
                ps = getattr(e, 'pos', '?')
                raise NameError(f"Erro semântico: chamada para '{fname}' com aridade {actual}, esperada {expected} (linha {ln}, pos {ps})")
            # verificar os argumentos recursivamente
            for a in args:
                check_expr(a, local_names, available_funs)
            return

        # Se chegar aqui: nó desconhecido — adaptar conforme sua AST
        return

    def check_stmt(s, local_names: Set[str], available_funs: Set[str]):
        # Assign: LHS deve já existir (em local_names OU global) e RHS não pode usar nomes não-declarados
        if isinstance(s, Assign):
            if s.nome not in local_names and s.nome not in symtab:
                ln = getattr(s, 'linha', '?')
                ps = getattr(s, 'pos', '?')
                raise NameError(f"Erro semântico: atribuição para variável não declarada '{s.nome}' (linha {ln}, pos {ps})")
            check_expr(s.expr, local_names, available_funs)
            return
        if isinstance(s, IfStmt):
            check_expr(s.cond, local_names, available_funs)
            for ss in s.then_stmts:
                check_stmt(ss, local_names, available_funs)
            if s.else_stmts is not None:
                for ss in s.else_stmts:
                    check_stmt(ss, local_names, available_funs)
            return
        if isinstance(s, WhileStmt):
            check_expr(s.cond, local_names, available_funs)
            for ss in s.body:
                check_stmt(ss, local_names, available_funs)
            return
        if isinstance(s, ReturnStmt):
            check_expr(s.expr, local_names, available_funs)
            return
        if isinstance(s, BlockStmt):
            for ss in s.stmts:
                check_stmt(ss, local_names, available_funs)
            return
        return

    # ---------- Checar cada função agora que assinaturas e offsets existem ----------
    # partial_funs permite chamadas para a própria função (recursão direta) e para funções já processadas
    partial_funs: Dict[str, FunDecl] = {}
    for f in fun_decls:
        # preparar conjuntos de nomes locais: params + locals
        params = getattr(f, 'params', [])
        locals_names = [d.nome for d in getattr(f, 'local_decls', [])]
        local_names = set(params) | set(locals_names)

        # checar conflitos parametro/local
        for lname in locals_names:
            if lname in params:
                raise NameError(f"Erro semântico: variável local '{lname}' redeclarada como parâmetro em função '{f.nome}'")

        # construir ambiente local inicial (somente nomes, valores simbólicos)
        # aqui usa local_names para verificação de nomes; as referências a funções são verificadas via partial_funs+symtab
        # define available_funs como as funções já em partial_funs mais a própria (permitir recursão direta)
        available_funs = set(partial_funs.keys()) | {f.nome}

        # checar inicializadores de declarações locais (podem usar params e globals e previously locals)
        local_env_names = set(params)  # nomes disponíveis no início para inicializadores
        for d in getattr(f, 'local_decls', []):
            # permitir que inicializador use params + previously declared locals + globals
            check_expr(d.expr, local_env_names | set(symtab.keys()), available_funs)
            if d.nome in local_env_names:
                raise NameError(f"Erro semântico: variável local '{d.nome}' redeclarada em função '{f.nome}'")
            local_env_names.add(d.nome)

        # checar comandos do corpo
        for c in getattr(f, 'comandos', []):
            check_stmt(c, local_names | set(symtab.keys()), available_funs)

        # checar expressão de retorno (resultado)
        ret_expr = getattr(f, 'resultado', None)
        if ret_expr is not None:
            check_expr(ret_expr, local_names | set(symtab.keys()), available_funs)

        # depois de tudo OK, registramos f em partial_funs para funções posteriores poderem chamá-la
        partial_funs[f.nome] = f

    # checar corpo do main (programa principal)
    # main não tem vardecl locais por sua restrição — parser já evita, checagem extra:
    main_locals = getattr(program, 'main_local_decls', [])
    if main_locals:
        raise NameError("Erro semântico: 'main' não pode conter variáveis locais (regra do projeto)")

    # verificar comandos do main (somente globals + chamadas para funções já definidas)
    # funs disponíveis no main são todas as funções definidas (partial_funs contém todas após a passada)
    available_funs_main = set(partial_funs.keys())
    for c in getattr(program, 'comandos', []):
        check_stmt(c, set(symtab.keys()), available_funs_main)

    if getattr(program, 'resultado', None) is not None:
        check_expr(program.resultado, set(symtab.keys()), available_funs_main)

    # tudo ok — retorna tabela de símbolos (e funções já têm param_offsets/local_offsets/frame_size)
    return symtab
