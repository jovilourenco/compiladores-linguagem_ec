# compiladores-linguagem_ec1

Aluno: João Victor Lourenço da Silva
Matrícula: 20220005997

Implementação de um compilador em Python para uma linguagem apenas de expressões constantes denominada "EC1". Projeto utilizado para avaliação na disciplina de Construção de Compiladores I. 

## Gramática da linguagem EC1

 A gramática para a linguagem EC1 é dada por: <br><br>
 programa ::= expressao <br>
 expressao ::= (expressao operador expressao) | literal-inteiro <br>
 operador ::= + |- | * | / <br>
 literal-inteiro ::= digito+ <br>
 digito ::= 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 <br>

## Etapas desenvolvidas durante a disciplina

Etapas implementadas:
1. Tokenização;
2. Analisador léxico (Tokenização) - Lexer;
3. Anailsador sintático - Parser;
4. Gerador de código.

## Estrutura de código

O código está dividido em 3 diretórios. 

- O diretório principal, contém os arquivos referentes às etapas, um `main.py` que servirá para executar todas as etapas de uma vez, e dois arquivos de teste: O arquivo `_teste.txt` possui a expressão que será executada pelo código, mas existem outros testes no arquivo `teste.txt` pré-definidos que podem ser utilizados na execução - Para usar, basta copiar e colar no arquivo `_teste.txt`. 
- O diretório 'assemblys' contém os modelos e é onde será criado o arquivo assembly `saida.s` após a geração do código (que será o código gerado de fato).
- O diretório 'helpers' contém as classes e módulos auxiliares que utilizei no código.

## Como executar

Para utilizar é bastante simples. Basta acessar o diretório principal no console e executar: 

python `main.py` _teste.txt

Esse comando printará cada etapa no console e gerará o código assembly correspondente para a expressão que está no arquivo `_teste.txt`.
Caso prefira rodar cada etapa separada, também é possível, basta usar o padrão:

python `nome_do_arquivo_da_etapa` _teste.txt

A saída será printada no console. Só o gerador não pode ser executado independentemente.

## Assembly

*Após rodar o código*, podemos compilar e executar o assembly gerado em `assemblys`. Para isso, podemos executar os seguintes comandos:

`cd assemblys` <br>
`as --64 -o saida.o saida.s` <br>
`ld -o saida saida.o` <br>
`./saida` <br>

Obs.: Assembly x86-64 AT&T

### Dúvidas para apresentação:

- Dada a expressão: ( 72 + a ), o analisador léxico indica o token com erro, mas não para a compilação. Logo, isso gerará, em seguida, erro sintático por não ter um formato de expressão que contenha a classe LEX_ERROR. Um erro sintático não gera o código assembly.