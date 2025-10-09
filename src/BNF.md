# BNF Completa MiniPar 2025.1 - Orientado a Objeto (Implementado)

```bnf
# ------------------- Programa Principal -------------------
<programa_minipar> ::= { <comentario> | <classe> | <funcao> | <declaracao_global> | <bloco_stmt> }

# ------------------- Comentários -------------------
<comentario> ::= "#" { <caractere_ate_fim_linha> }

# ------------------- Funções -------------------
<funcao> ::= <tipo_retorno> <identificador> "(" [ <parametros> ] ")" "{" <stmts_lista> "}"

<parametros> ::= <parametro> { "," <parametro> }

<parametro> ::= <tipo_var> <identificador> [ "[" "]" ]  # Suporte a arrays como parâmetros

<tipo_retorno> ::= "void" | "int" | "float" | "string" | "bool" | <identificador>

<tipo_var> ::= "int" | "float" | "string" | "bool" | "c_channel" | <identificador>

# ------------------- Classes -------------------
<classe> ::= "class" <identificador> [ "extends" <identificador> ] 
            "{" 
                { <declaracao_atributo> } 
                { <declaracao_metodo> } 
            "}"

<declaracao_atributo> ::= <tipo_var> <identificador> [ <dimensao_array> ] [ ";" ]

<dimensao_array> ::= "[" [ <expr> ] "]" [ "[" [ <expr> ] "]" ]  # Suporte a arrays 1D e 2D

<declaracao_metodo> ::= <tipo_retorno> <identificador> "(" [ <parametros> ] ")" "{" <stmts_lista> "}"

# ------------------- Declarações -------------------
<declaracao_global> ::= <tipo_var> <identificador> [ <dimensao_array> ] [ "=" <inicializacao> ] [ ";" ]

<inicializacao> ::= <expr> 
                  | "[" <lista_valores> "]"  # Inicialização de array
                  | "{" <lista_valores> "}"  # Inicialização com chaves

<lista_valores> ::= <expr> { "," <expr> }

# ------------------- Blocos SEQ/PAR -------------------
<bloco_stmt> ::= ( "seq" | "par" ) "{" <stmts_lista> "}"

<stmts_lista> ::= { <stmt> }

<stmt> ::= <declaracao>
         | <atribuicao>
         | <atribuicao_array>
         | <atribuicao_atributo>
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
         | <return_stmt>
         | <bloco_stmt>        # Blocos aninhados
         | <comentario>
         | <acesso_this>

# ------------------- Comandos Básicos -------------------
<declaracao> ::= <tipo_var> <identificador> [ <dimensao_array> ] [ "=" <inicializacao> ] [ ";" ]

<atribuicao> ::= <identificador> "=" <expr> [ ";" ]

<atribuicao_array> ::= <identificador> "[" <expr> "]" [ "[" <expr> "]" ] "=" <expr> [ ";" ]

<atribuicao_atributo> ::= <identificador> "." <identificador> "=" <expr> [ ";" ]
                        | "this" "." <identificador> "=" <expr> [ ";" ]
                        | "this" "." <identificador> "[" <expr> "]" [ "[" <expr> "]" ] "=" <expr> [ ";" ]

<acesso_this> ::= "this" "." <identificador> 
                | "this" "." <identificador> "[" <expr> "]" [ "[" <expr> "]" ]
                | "this" "." <identificador> "(" [ <argumentos> ] ")"

# ------------------- Estruturas de Controle -------------------
<if_stmt> ::= "if" <condicao> "{" <stmts_lista> "}" 
             [ "else" ( "if" <condicao> "{" <stmts_lista> "}" | "{" <stmts_lista> "}" ) ]

<while_stmt> ::= "while" <condicao> "{" <stmts_lista> "}"

<for_stmt> ::= "for" <identificador> "=" <expr> ";" <condicao> ";" 
               <identificador> "=" <expr> "{" <stmts_lista> "}"

# ------------------- Orientação a Objetos -------------------
<instanciacao> ::= <identificador> <identificador> "=" "new" <identificador> "(" ")" [ ";" ]

<chamada_metodo> ::= <identificador> "." <identificador> "(" [ <argumentos> ] ")" [ ";" ]
                   | <identificador> "." "send" "(" <argumentos> ")" [ ";" ]
                   | <identificador> "." "receive" "(" <lista_identificadores> ")" [ ";" ]

<chamada_funcao> ::= <identificador> "(" [ <argumentos> ] ")" [ ";" ]

<argumentos> ::= <expr> { "," <expr> }

<lista_identificadores> ::= <identificador> { "," <identificador> }

# ------------------- Comandos de I/O -------------------
<print_comando> ::= "print" "(" <expr> ")" [ ";" ]

<input_comando> ::= <identificador> "=" "input" "(" [ <expr> ] ")" [ ";" ]

<return_stmt> ::= "return" <expr> [ ";" ]

# ------------------- Comunicação (Canais) -------------------
<send> ::= <identificador> "." "send" "(" <argumentos> ")" [ ";" ]

<receive> ::= <identificador> "." "receive" "(" <lista_identificadores> ")" [ ";" ]

# ------------------- Expressões -------------------
<condicao> ::= <expr_logica_and>

<expr_logica_and> ::= <expr_logica_or> { "&&" <expr_logica_or> }

<expr_logica_or> ::= <expr_relacional> { "||" <expr_relacional> }

<expr_relacional> ::= <expr> [ <operador_relacional> <expr> ]

<expr> ::= <expr_aditivo>

<expr_aditivo> ::= <expr_multiplicativo> { ( "+" | "-" ) <expr_multiplicativo> }

<expr_multiplicativo> ::= <expr_unario> { ( "*" | "/" ) <expr_unario> }

<expr_unario> ::= <numero>
                | <texto>
                | <identificador>
                | <identificador> "[" <expr> "]" [ "[" <expr> "]" ]
                | <identificador> "." <identificador>
                | <identificador> "." <identificador> "(" [ <argumentos> ] ")"
                | <identificador> "(" [ <argumentos> ] ")"
                | "this" "." <identificador>
                | "this" "." <identificador> "[" <expr> "]" [ "[" <expr> "]" ]
                | "new" <identificador> "(" ")"
                | "(" <expr> ")"
                | "-" <expr_unario>
                | <funcao_string>

<funcao_string> ::= ( "strlen" | "substr" | "charat" | "indexof" | "parseint" ) "(" <argumentos> ")"

<operador_relacional> ::= "==" | "!=" | ">" | "<" | ">=" | "<="

# ------------------- Literais e Identificadores -------------------
<identificador> ::= ( <letra> | "_" ) { <letra> | <digito> | "_" }

<texto> ::= '"' { <caractere> } '"'

<numero> ::= <digito> { <digito> } [ "." <digito> { <digito> } ]

<letra> ::= "A" | ... | "Z" | "a" | ... | "z"

<digito> ::= "0" | ... | "9"

<caractere> ::= qualquer caractere visível exceto '"' (com suporte a escape no futuro)

<caractere_ate_fim_linha> ::= qualquer caractere exceto '\n'
```
