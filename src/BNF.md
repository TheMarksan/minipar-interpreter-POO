# BNF Completa MiniPar 2025.1 - Orientado a Objeto

```bnf
<programa_minipar> ::= { <comentario> | <classe> | <funcao> }

# ------------------- Comentários -------------------
<comentario> ::= "#" { <caractere> }

# ------------------- Funções -------------------
<funcao> ::= <tipo_retorno> <identificador>() { <bloco_stmt> }

# ------------------- Classes -------------------
<classe> ::= class <identificador> [ extends <identificador> ] 
            { 
                { <declaracao_atributo> } 
                { <declaracao_metodo> } 
            }

<declaracao_atributo> ::= <tipo_var> <identificador>

<declaracao_metodo> ::= <tipo_retorno> <identificador>() { <bloco_stmt> }

<tipo_retorno> ::= void | int | float | string | <identificador>

<tipo_var> ::= bool | int | float | string | <identificador> | c_channel

# ------------------- Blocos SEQ/PAR aninháveis -------------------
<bloco_stmt> ::= seq { <stmts_lista> } 
               | par { <stmts_lista> }

<stmts_lista> ::= { <stmts> }

<stmts> ::= <atribuicao>
          | <if_stmt>
          | <while_stmt>
          | <for_stmt>
          | <instanciacao>
          | <chamada_metodo>
          | <chamada_funcao>
          | <print_comando>
          | <input_comando>
          | <send>
          | <receive>
          | <bloco_stmt>     # Permite blocos SEQ/PAR dentro de outros blocos
          | <comentario>

# ------------------- Comandos -------------------
<atribuicao> ::= <identificador> = <expr>

<if_stmt> ::= if <condicao> { <stmts_lista> } [ else { <stmts_lista> } ]

<while_stmt> ::= while <condicao> { <stmts_lista> }

<for_stmt> ::= for <identificador> = <expr>; <condicao>; <incremento> { <stmts_lista> }

<instanciacao> ::= <identificador> <identificador> = new <identificador>()

<chamada_metodo> ::= <identificador>.<identificador>()

<chamada_funcao> ::= <identificador>() 

<print_comando> ::= print( <texto> | <expr> )

<input_comando> ::= <identificador> = input( [ <texto> ] )

<send> ::= <identificador>.send( { <expr> | <identificador> }+ )

<receive> ::= <identificador>.receive( { <identificador> }+ )

# ------------------- Expressões -------------------
<expr> ::= <expr_aditivo>

<expr_aditivo> ::= <expr_aditivo> + <expr_multiplicativo>
                 | <expr_aditivo> - <expr_multiplicativo>
                 | <expr_multiplicativo>

<expr_multiplicativo> ::= <expr_multiplicativo> * <expr_unario>
                        | <expr_multiplicativo> / <expr_unario>
                        | <expr_unario>

<expr_unario> ::= <numero> | <identificador> | ( <expr> )

<condicao> ::= <expr> <operador_relacional> <expr>

<incremento> ::= <identificador> = <identificador> + <numero>

<operador_relacional> ::= == | != | > | < | >= | <=

# ------------------- Identificadores e Literais -------------------
<identificador> ::= <letra> { <letra> | <digito> }

<texto> ::= "{" { <caractere> } "}"

<numero> ::= <digito> { <digito> } [ . <digito>+ ]

<letra> ::= "A" | ... | "Z" | "a" | ... | "z"

<digito> ::= "0" | ... | "9"

<caractere> ::= qualquer símbolo visível (exceto aspas internas)
