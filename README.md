# compiladores-linguagem_ec1
Implementação de um compilador em Python para uma linguagem apenas de expressões constantes. Projeto utilizado para obtenção de nota na disciplina de Construção de Compiladores I. 

 A gramática para a linguagem EC1 é:
 programa ::= expressao
 expressao ::= (expressao operador expressao) | literal-inteiro
 operador ::= + |- | * | /
 literal-inteiro ::= digito+
 digito ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9

 Etapas implementadas:
 1. Analisador léxico (Tokenização) - Lexer;
 2. Anailsador sintático - Parser;
 3. Interpretador - Interpreter.

### Como usar

Para utilizar é bastante simples. Basta acessar o diretório no console e executar: 

python `main.py` _teste.txt

O arquivo `_teste.txt` possui a expressão que será executada, mas existem outros testes no arquivo `teste.txt` que podem ser utilizados na execução.
