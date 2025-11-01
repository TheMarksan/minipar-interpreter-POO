#!/usr/bin/env python3
"""
Script para testar todos os exemplos rápidos do frontend
"""
import sys
sys.path.insert(0, 'src')

from lexer.Lexer import Lexer
from parser.Parser import Parser
from semantic.SemanticAnalyzer import SemanticAnalyzer

# Todos os exemplos rápidos do frontend
examples = {
    # === BÁSICO ===
    'Hello World': '''SEQ {
    print("Hello, World!\\n");
    print("Bem-vindo ao MiniPar!\\n");
}''',
    
    'Variáveis e Tipos': '''SEQ {
    INT idade;
    FLOAT altura;
    STRING nome;
    BOOL ativo;
    
    idade = 25;
    altura = 1.75;
    nome = "Maria";
    ativo = 1;
    
    print("Nome: " + nome + "\\n");
    print("Idade: " + idade + "\\n");
    print("Altura: " + altura + "\\n");
}''',
    
    'Print & Operações Aritméticas': '''SEQ {
    print("Soma: " + (10 + 5) + "\\n");
    print("Subtração: " + (10 - 3) + "\\n");
    print("Multiplicação: " + (4 * 7) + "\\n");
    print("Divisão: " + (20 / 4) + "\\n");
    print("Potência: " + (2 * 2 * 2) + "\\n");
}''',
    
    # === CONTROLE DE FLUXO ===
    'If-Else': '''SEQ {
    INT nota;
    nota = 75;
    
    if (nota >= 90) {
        print("Excelente!\\n");
    } else if (nota >= 70) {
        print("Bom!\\n");
    } else if (nota >= 50) {
        print("Regular\\n");
    } else {
        print("Reprovado\\n");
    }
}''',
    
    'Variables & If': '''SEQ {
    INT x;
    INT y;
    x = 10;
    y = 5;
    if (x > y) {
        print("x é maior\\n");
    } else {
        print("y é maior ou igual\\n");
    }
}''',
    
    'Switch Case': '''SEQ {
    INT opcao;
    opcao = 2;
    
    if (opcao == 1) {
        print("Opção 1: Novo\\n");
    } else if (opcao == 2) {
        print("Opção 2: Abrir\\n");
    } else if (opcao == 3) {
        print("Opção 3: Salvar\\n");
    } else {
        print("Opção inválida\\n");
    }
}''',
    
    # === LOOPS ===
    'For Loop': '''SEQ {
    INT i;
    INT soma;
    soma = 0;
    
    for i = 1; i <= 5; i = i + 1 {
        print("i = " + i + "\\n");
        soma = soma + i;
    }
    print("Soma total: " + soma + "\\n");
}''',
    
    'While Loop': '''SEQ {
    INT contador;
    contador = 5;
    
    while (contador > 0) {
        print("Contagem: " + contador + "\\n");
        contador = contador - 1;
    }
    print("FIM!\\n");
}''',
    
    'Loops & Functions': '''SEQ {
    INT soma(INT a, INT b) {
        return a + b;
    }
    
    INT i;
    for i = 0; i < 3; i = i + 1 {
        print("Loop " + i + ": soma = " + soma(i, 10) + "\\n");
    }
}''',
    
    'Loop Aninhado': '''SEQ {
    INT i;
    INT j;
    INT matriz[3][3];
    
    for i = 0; i < 3; i = i + 1 {
        for j = 0; j < 3; j = j + 1 {
            matriz[i][j] = i * 3 + j;
            print(matriz[i][j] + " ");
        }
        print("\\n");
    }
}''',
    
    # === FUNÇÕES ===
    'Função Simples': '''SEQ {
    INT dobro(INT n) {
        return n * 2;
    }
    
    FLOAT media(FLOAT a, FLOAT b) {
        return (a + b) / 2.0;
    }
    
    print("Dobro de 7: " + dobro(7) + "\\n");
    print("Média 8 e 6: " + media(8.0, 6.0) + "\\n");
}''',
    
    'Função Recursiva': '''SEQ {
    INT fibonacci(INT n) {
        if (n <= 1) {
            return n;
        }
        return fibonacci(n - 1) + fibonacci(n - 2);
    }
    
    INT i;
    print("Sequência Fibonacci:\\n");
    for i = 0; i < 8; i = i + 1 {
        print(fibonacci(i) + " ");
    }
    print("\\n");
}''',
    
    'Múltiplas Funções': '''SEQ {
    INT fatorial(INT n) {
        if (n <= 1) return 1;
        return n * fatorial(n - 1);
    }
    
    BOOL ehPar(INT n) {
        return (n - (n / 2) * 2) == 0;
    }
    
    print("5! = " + fatorial(5) + "\\n");
    print("10 é par? " + ehPar(10) + "\\n");
    print("7 é par? " + ehPar(7) + "\\n");
}''',
    
    # === ARRAYS ===
    'Array Básico': '''SEQ {
    INT numeros[5];
    INT i;
    INT soma;
    
    numeros[0] = 10;
    numeros[1] = 20;
    numeros[2] = 30;
    numeros[3] = 40;
    numeros[4] = 50;
    
    soma = 0;
    for i = 0; i < 5; i = i + 1 {
        soma = soma + numeros[i];
    }
    print("Soma do array: " + soma + "\\n");
}''',
    
    'Array Multidimensional': '''SEQ {
    INT matriz[2][3];
    INT i;
    INT j;
    
    # Preencher matriz
    for i = 0; i < 2; i = i + 1 {
        for j = 0; j < 3; j = j + 1 {
            matriz[i][j] = (i + 1) * (j + 1);
        }
    }
    
    # Imprimir matriz
    print("Matriz 2x3:\\n");
    for i = 0; i < 2; i = i + 1 {
        for j = 0; j < 3; j = j + 1 {
            print(matriz[i][j] + " ");
        }
        print("\\n");
    }
}''',
    
    # === POO ===
    'Classe Simples': '''class Pessoa {
    STRING nome;
    INT idade;
    
    VOID setDados(STRING n, INT i) {
        this.nome = n;
        this.idade = i;
    }
    
    VOID apresentar() {
        print("Olá! Meu nome é " + this.nome);
        print(" e tenho " + this.idade + " anos.\\n");
    }
}

SEQ {
    Pessoa p;
    p = new Pessoa();
    p.setDados("João", 30);
    p.apresentar();
}''',
    
    'Herança': '''class Animal {
    STRING nome;
    
    VOID setNome(STRING n) {
        this.nome = n;
    }
}

class Cachorro extends Animal {
    VOID latir() {
        print(this.nome + " diz: Au au!\\n");
    }
}

SEQ {
    Cachorro dog;
    dog = new Cachorro();
    dog.setNome("Rex");
    dog.latir();
}''',
    
    # === THREADS ===
    'Hello World Threads': '''SEQ {
    VOID thread1() {
        INT i;
        for i = 0; i < 3; i = i + 1 {
            print("Thread A: " + i + "\\n");
        }
    }
    
    VOID thread2() {
        INT j;
        for j = 5; j < 8; j = j + 1 {
            print("Thread B: " + j + "\\n");
        }
    }
    
    PAR {
        thread1();
        thread2();
    }
}''',
    
    'PAR Block': '''SEQ {
    VOID tarefa1() {
        print("Tarefa 1 iniciada\\n");
        INT i;
        for i = 0; i < 3; i = i + 1 {
            print("T1: processando...\\n");
        }
        print("Tarefa 1 concluída\\n");
    }
    
    VOID tarefa2() {
        print("Tarefa 2 iniciada\\n");
        INT j;
        for j = 0; j < 3; j = j + 1 {
            print("T2: executando...\\n");
        }
        print("Tarefa 2 concluída\\n");
    }
    
    PAR {
        tarefa1();
        tarefa2();
    }
}''',
    
    # === CANAIS ===
    'Channels Send/Receive': '''SEQ {
    C_CHANNEL canal;
    canal.send(42);
    canal.send(100);
    print("Valores enviados para o canal\\n");
}''',
    
    'Canal com Loop': '''SEQ {
    C_CHANNEL resultados;
    INT i;
    
    for i = 1; i <= 5; i = i + 1 {
        resultados.send(i * 10);
    }
    print("Enviados 5 valores para o canal\\n");
}''',
    
    'Múltiplos Canais': '''SEQ {
    C_CHANNEL canal_A;
    C_CHANNEL canal_B;
    
    canal_A.send(10);
    canal_A.send(20);
    
    canal_B.send(30);
    canal_B.send(40);
    
    print("Valores enviados em 2 canais\\n");
}''',
    
    # === STRINGS ===
    'String Básico': '''SEQ {
    STRING mensagem;
    STRING nome;
    
    nome = "MiniPar";
    mensagem = "Bem-vindo ao " + nome + "!";
    
    print(mensagem + "\\n");
}''',
    
    'Funções String': '''SEQ {
    STRING texto;
    INT tamanho;
    STRING parte;
    
    texto = "Programacao";
    tamanho = strlen(texto);
    parte = substr(texto, 0, 7);
    
    print("Texto: " + texto + "\\n");
    print("Tamanho: " + tamanho + "\\n");
    print("Substring: " + parte + "\\n");
}'''
}

def test_example(name, code):
    """Testa um único exemplo"""
    try:
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse()
        
        analyzer = SemanticAnalyzer()
        result = analyzer.analyze(ast)
        
        return {
            'success': result['success'],
            'errors': result.get('errors', []),
            'warnings': result.get('warnings', []),
            'stats': result.get('statistics', {})
        }
    except Exception as e:
        return {
            'success': False,
            'errors': [str(e)],
            'warnings': [],
            'stats': {}
        }

def main():
    print("=" * 80)
    print(" TESTE DE TODOS OS EXEMPLOS RÁPIDOS DO FRONTEND")
    print("=" * 80)
    print()
    
    # Organizar exemplos por categoria
    categories = {
        '📝 Básico': ['Hello World', 'Variáveis e Tipos', 'Print & Operações Aritméticas'],
        '🔀 Controle de Fluxo': ['If-Else', 'Variables & If', 'Switch Case'],
        '🔁 Loops': ['For Loop', 'While Loop', 'Loops & Functions', 'Loop Aninhado'],
        '🔧 Funções': ['Função Simples', 'Função Recursiva', 'Múltiplas Funções'],
        '📚 Arrays': ['Array Básico', 'Array Multidimensional'],
        '🏛️ POO': ['Classe Simples', 'Herança'],
        '🧵 Threads': ['Hello World Threads', 'PAR Block'],
        '📡 Canais': ['Channels Send/Receive', 'Canal com Loop', 'Múltiplos Canais'],
        '🎯 Strings': ['String Básico', 'Funções String']
    }
    
    all_results = []
    
    for category, example_names in categories.items():
        print(f"\n{category}")
        print("-" * 80)
        
        for name in example_names:
            if name not in examples:
                print(f"  ❌ {name:45} | NÃO ENCONTRADO")
                continue
            
            result = test_example(name, examples[name])
            all_results.append((name, result))
            
            if result['success']:
                stats = result['stats']
                total_errs = stats.get('total_errors', 0)
                total_warns = stats.get('total_warnings', 0)
                print(f"  ✅ {name:45} | Erros: {total_errs:2d}  Avisos: {total_warns:2d}")
            else:
                error_count = len(result['errors'])
                print(f"  ❌ {name:45} | {error_count} erro(s)")
                for err in result['errors'][:2]:  # Mostra primeiros 2 erros
                    print(f"      → {err[:70]}")
                if len(result['errors']) > 2:
                    print(f"      → ... e mais {len(result['errors']) - 2} erro(s)")
    
    # Resumo
    print()
    print("=" * 80)
    success_count = sum(1 for _, r in all_results if r['success'])
    total_count = len(all_results)
    percentage = (100 * success_count // total_count) if total_count > 0 else 0
    
    print(f" RESUMO FINAL: {success_count}/{total_count} exemplos passaram ({percentage}%)")
    print("=" * 80)
    
    # Listar falhas
    failures = [(name, r) for name, r in all_results if not r['success']]
    if failures:
        print()
        print(f"⚠️  EXEMPLOS COM PROBLEMAS ({len(failures)}):")
        print()
        for name, result in failures:
            print(f"  📄 {name}")
            for err in result['errors'][:3]:
                print(f"     • {err}")
            if len(result['errors']) > 3:
                print(f"     • ... e mais {len(result['errors']) - 3} erro(s)")
            print()
    
    return 0 if success_count == total_count else 1

if __name__ == '__main__':
    sys.exit(main())
