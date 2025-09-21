# BNF Completa MiniPar 2025.1 - Orientado a Objeto

```bnf
<programa_minipar> ::= { <classe> }

# ------------------- Classes -------------------
<classe>           ::= CLASS <identificador> [ EXTENDS <identificador> ] { { <declaracao_atributo> } { <declaracao_metodo> } }

<declaracao_atributo> ::= <tipo_var> <identificador>

<declaracao_metodo>   ::= <tipo_retorno> <identificador>() { <bloco_stmt> }

<tipo_retorno>        ::= VOID | INT | FLOAT | STRING | <identificador>  # tipo de classe permitido

<tipo_var>            ::= BOOL | INT | FLOAT | STRING | <identificador>  # variáveis ou canal de comunicação
       
# ------------------- Blocos SEQ/PAR -------------------
<bloco_stmt>         ::= <bloco_SEQ> | <bloco_PAR>

<bloco_SEQ>          ::= SEQ { { <stmts> } }

<bloco_PAR>          ::= PAR { { <stmts> } }

# ------------------- Comandos -------------------
<stmts>              ::= <atribuicao>
                       | <if_stmt>
                       | <while_stmt>
                       | <for_stmt>
                       | <instanciacao>
                       | <chamada_metodo>
                       | <print_comando>
                       | <send>
                       | <receive>

<atribuicao>         ::= <identificador> = <expr>

<if_stmt>            ::= IF <condicao> { { <stmts> } } [ ELSE { { <stmts> } } ]

<while_stmt>         ::= WHILE <condicao> { { <stmts> } }

<for_stmt>           ::= FOR <identificador> = <expr>; <condicao>; <incremento> { { <stmts> } }

<instanciacao>       ::= <identificador> <identificador> = NEW <identificador>()

<chamada_metodo>     ::= <identificador>.<identificador>()

<print_comando>      ::= PRINT ( <texto> )

<send>               ::= <identificador>.SEND( { <expr> | <identificador> }+ )

<receive>            ::= <identificador>.RECEIVE( { <identificador> }+ )

# ------------------- Expressões -------------------
<expr>               ::= <numero>
                       | <identificador>
                       | <expr> + <expr>
                       | <expr> - <expr>
                       | <expr> * <expr>
                       | <expr> / <expr>

<condicao>           ::= <expr> <operador_relacional> <expr>

<incremento>         ::= <identificador> = <identificador> + <numero>

<operador_relacional> ::= == | != | > | < | >= | <=

# ------------------- Identificadores e Literais -------------------
<identificador>      ::= <letra> { <letra> | <digito> }

<texto>              ::= "{" { <caractere> } "}"

<numero>             ::= <digito> { <digito> } [ . <digito>+ ]

<letra>              ::= "A" | ... | "Z" | "a" | ... | "z"

<digito>             ::= "0" | ... | "9"

<caractere>          ::= qualquer símbolo visível (exceto aspas internas)
