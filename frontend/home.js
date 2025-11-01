document.addEventListener('DOMContentLoaded', () => {
  const codeEl = document.getElementById('code');
  const gutter = document.getElementById('gutter');
  const runBtn = document.getElementById('runBtn');
  const clearBtn = document.getElementById('clearBtn');
  const sampleBtn = document.getElementById('sampleBtn');
  const execOut = document.getElementById('execOutput');
  const lexOut = document.getElementById('lexOutput');
  const semOut = document.getElementById('semOutput');
  const tacOut = document.getElementById('tacOutput');
  const symbolTableOut = document.getElementById('symbolTableOutput');
  const tokCount = document.getElementById('tokCount');
  const status = document.getElementById('status');
  const exportBtn = document.getElementById('exportBtn');
  const themeSel = document.getElementById('themeSel');
  const astViewToggle = document.getElementById('astViewToggle');
  let currentRunId = null;
  
  // AST view mode state (persistente no localStorage)
  let astViewMode = localStorage.getItem('astViewMode') || 'tree'; // 'tree' ou 'text'
  let currentAstData = null; // Armazena os dados da AST atual

  function getEditorValue(){ return (window.editorInstance && window.editorInstance.getValue) ? window.editorInstance.getValue() : codeEl.value }
  function setEditorValue(v){ if(window.editorInstance && window.editorInstance.setValue) window.editorInstance.setValue(v); else codeEl.value = v }
  function updateGutter(){
    // Preferir lineCount do CodeMirror se presente
    const lines = (window.editorInstance && window.editorInstance.lineCount) ? window.editorInstance.lineCount() : getEditorValue().split('\n').length || 1;
    let s=''; for(let i=1;i<=lines;i++) s += i + '\n';
    if(gutter) gutter.textContent = s;
  }

  // Exemplo padrão e exemplos (seguindo a sintaxe MiniPar)
  const sample = `# Exemplo MiniPar
SEQ {
    INT x;
    x = 10;
    print("Valor de x: " + x + "\\n");
}
`;
  const examples = {
    // === BÁSICO ===
    'Hello World': `SEQ {
    print("Hello, World!\\n");
    print("Bem-vindo ao MiniPar!\\n");
}`,
    
    'Variáveis e Tipos': `SEQ {
    INT idade;
    FLOAT altura;
    STRING nome;
    
    idade = 25;
    altura = 1.75;
    nome = "Maria";
    
    print("Nome: " + nome + "\\n");
    print("Idade: " + idade + "\\n");
    print("Altura: " + altura + "\\n");
}`,
    
    'Print & Operações Aritméticas': `SEQ {
    print("Soma: " + (10 + 5) + "\\n");
    print("Subtração: " + (10 - 3) + "\\n");
    print("Multiplicação: " + (4 * 7) + "\\n");
    print("Divisão: " + (20 / 4) + "\\n");
    print("Potência: " + (2 * 2 * 2) + "\\n");
}`,
    
    // === CONTROLE DE FLUXO ===
    'If-Else': `SEQ {
    INT nota;
    nota = 75;
    
    if nota >= 90 {
        print("Excelente!\\n");
    } else if nota >= 70 {
        print("Bom!\\n");
    } else if nota >= 50 {
        print("Regular\\n");
    } else {
        print("Reprovado\\n");
    }
}`,
    
    'Variables & If': `SEQ {
    INT x;
    INT y;
    x = 10;
    y = 5;
    if x > y {
        print("x é maior\\n");
    } else {
        print("y é maior ou igual\\n");
    }
}`,
    
    'Switch Case (múltiplos If)': `SEQ {
    INT opcao;
    opcao = 2;
    
    if opcao == 1 {
        print("Opção 1: Novo\\n");
    } else if opcao == 2 {
        print("Opção 2: Abrir\\n");
    } else if opcao == 3 {
        print("Opção 3: Salvar\\n");
    } else {
        print("Opção inválida\\n");
    }
}`,
    
    // === LOOPS ===
    'For Loop': `SEQ {
    INT i;
    INT soma;
    soma = 0;
    
    for i = 1; i <= 5; i = i + 1 {
        print("i = " + i + "\\n");
        soma = soma + i;
    }
    print("Soma total: " + soma + "\\n");
}`,
    
    'While Loop': `SEQ {
    INT contador;
    contador = 5;
    
    while contador > 0 {
        print("Contagem: " + contador + "\\n");
        contador = contador - 1;
    }
    print("FIM!\\n");
}`,
    
    'Loops & Functions': `SEQ {
    INT soma(INT a, INT b) {
        return a + b;
    }
    
    INT i;
    for i = 0; i < 3; i = i + 1 {
        print("Loop " + i + ": soma = " + soma(i, 10) + "\\n");
    }
}`,
    
    'Loop Aninhado (matriz)': `SEQ {
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
}`,
    
    // === FUNÇÕES ===
    'Função Simples': `INT dobro(INT n) {
    return n * 2;
}

FLOAT media(FLOAT a, FLOAT b) {
    return (a + b) / 2.0;
}

SEQ {
    print("Dobro de 7: " + dobro(7) + "\\n");
    print("Média 8 e 6: " + media(8.0, 6.0) + "\\n");
}`,
    
    'Função Recursiva (Fibonacci)': `INT fibonacci(INT n) {
    if n <= 1 {
        return n;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

SEQ {
    INT i;
    print("Sequência Fibonacci:\\n");
    for i = 0; i < 8; i = i + 1 {
        print(fibonacci(i) + " ");
    }
    print("\\n");
}`,
    
    'Múltiplas Funções': `INT fatorial(INT n) {
    if n <= 1 {
        return 1;
    }
    return n * fatorial(n - 1);
}

INT ehPar(INT n) {
    INT resto;
    resto = n - (n / 2) * 2;
    if resto == 0 {
        return 1;
    }
    return 0;
}

SEQ {
    print("5! = " + fatorial(5) + "\\n");
    print("10 é par? " + ehPar(10) + "\\n");
    print("7 é par? " + ehPar(7) + "\\n");
}`,
    
    // === ARRAYS ===
    'Array Básico': `SEQ {
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
}`,
    
    'Array Multidimensional': `SEQ {
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
}`,
    
    // === POO ===
    'Classe Simples': `class Pessoa {
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
}`,
    
    'Herança (extends)': `class Animal {
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
}`,
    
    // === THREADS ===
    'Hello World (threads)': `VOID thread1() {
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

SEQ {
    PAR {
        thread1();
        thread2();
    }
}`,
    
    'PAR Block': `VOID tarefa1() {
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

SEQ {
    PAR {
        tarefa1();
        tarefa2();
    }
}`,
    
    // === CANAIS ===
    'Channels Send/Receive': `SEQ {
    C_CHANNEL canal;
    canal.send(42);
    canal.send(100);
    print("Valores enviados para o canal\\n");
}`,
    
    'Canal com Loop': `SEQ {
    C_CHANNEL resultados;
    INT i;
    
    for i = 1; i <= 5; i = i + 1 {
        resultados.send(i * 10);
    }
    print("Enviados 5 valores para o canal\\n");
}`,
    
    'Múltiplos Canais': `SEQ {
    C_CHANNEL canal_A;
    C_CHANNEL canal_B;
    
    canal_A.send(10);
    canal_A.send(20);
    
    canal_B.send(30);
    canal_B.send(40);
    
    print("Valores enviados em 2 canais\\n");
}`,
    
    // === STRINGS ===
    'String Básico': `SEQ {
    STRING mensagem;
    STRING nome;
    
    nome = "MiniPar";
    mensagem = "Bem-vindo ao " + nome + "!";
    
    print(mensagem + "\\n");
}`,
    
    'Funções String (strlen, substr)': `SEQ {
    STRING texto;
    INT tamanho;
    STRING parte;
    
    texto = "Programacao";
    tamanho = strlen(texto);
    parte = substr(texto, 0, 7);
    
    print("Texto: " + texto + "\\n");
    print("Tamanho: " + tamanho + "\\n");
    print("Substring: " + parte + "\\n");
}`,
    
    // === INPUT (novo) ===
    'Input Básico': `SEQ {
    STRING nome;
    INT idade;
    
    print("Digite seu nome: ");
    nome = input();
    print("Olá, " + nome + "!\\n");
    
    print("Digite sua idade: ");
    idade = input();
    print("Você tem " + idade + " anos.\\n");
}`,
    
    'Input com Cálculo': `SEQ {
    INT num1;
    INT num2;
    INT soma;
    
    print("Primeiro número: ");
    num1 = input();
    print("Segundo número: ");
    num2 = input();
    
    soma = num1 + num2;
    print("A soma é: " + soma + "\\n");
}`,
    
    'Input em Loop': `SEQ {
    INT i;
    INT numero;
    INT soma;
    
    soma = 0;
    for i = 1; i <= 3; i = i + 1 {
        print("Digite o número " + i + ": ");
        numero = input();
        soma = soma + numero;
    }
    print("Soma total: " + soma + "\\n");
}`
  };

  // Carregar exemplo
  sampleBtn.addEventListener('click', async ()=>{
    const sel = document.getElementById('exampleSel');
    const value = sel?.value;
    
    if (!value) {
      setEditorValue(sample);
      status.textContent = 'Exemplo carregado';
      updateGutter();
      setTimeout(()=>status.textContent='Pronto',800);
      return;
    }
    
    // Exemplos embutidos
    if (examples[value]) {
      setEditorValue(examples[value]);
      status.textContent = `Exemplo: ${value} carregado`;
      updateGutter();
      setTimeout(()=>status.textContent='Pronto',800);
      return;
    }
    
    // Exemplos de arquivos
    const fileMap = {
      'Neuronio (POO)': '../tests/programa3_neuronio.minipar',
      'Quicksort (arrays/POO)': '../tests/programa6_quicksort.minipar',
      'Threads - cliente/servidor (programa2)': '../tests/programa2_threads.minipar',
      'Sistema Recomendação': '../tests/programa5_recomendacao.minipar'
    };
    
    if (fileMap[value]) {
      try {
        status.textContent = 'Carregando arquivo...';
        const resp = await fetch(fileMap[value]);
        if (resp.ok) {
          const code = await resp.text();
          setEditorValue(code);
          status.textContent = `Arquivo: ${value} carregado`;
          updateGutter();
          setTimeout(()=>status.textContent='Pronto',1000);
        } else {
          status.textContent = 'Erro ao carregar arquivo';
          setTimeout(()=>status.textContent='Pronto',1500);
        }
      } catch (e) {
        console.error('Erro ao carregar arquivo:', e);
        status.textContent = 'Erro ao carregar';
        setTimeout(()=>status.textContent='Pronto',1500);
      }
    }
  });

  clearBtn.addEventListener('click', ()=>{ setEditorValue(''); updateGutter(); execOut.textContent=''; lexOut.textContent=''; semOut.textContent=''; tokCount.textContent='0'; status.textContent='Limpo'; setTimeout(()=>status.textContent='Pronto',600)});

  // Alternar tema (aplicar classe ao textarea)
  function applyTheme(theme){
    // theme = 'light' ou 'dark'
    if(theme === 'light'){
      document.body.classList.remove('dark-theme'); document.body.classList.add('light-theme');
      if(window.editorInstance) window.editorInstance.setOption('theme','default');
    } else {
      document.body.classList.remove('light-theme'); document.body.classList.add('dark-theme');
      if(window.editorInstance) window.editorInstance.setOption('theme','dracula');
    }
  }
  themeSel.addEventListener('change', (e)=>{ applyTheme(e.target.value); });

  // Renderizar AST (tree ou text mode)
  function renderAST(astData, mode = null) {
    const astOutput = document.getElementById('astOutput');
    if (!astOutput) return;
    
    if (!astData) {
      astOutput.textContent = 'Nenhuma árvore sintática gerada.';
      return;
    }
    
    // Usar o modo especificado ou o modo atual
    const viewMode = mode || astViewMode;
    
    // Armazenar dados atuais para permitir toggle
    currentAstData = astData;
    
    if (!window.ASTTreeRenderer) {
      // Fallback: mostrar como JSON
      astOutput.textContent = typeof astData === 'string' ? astData : JSON.stringify(astData, null, 2);
      return;
    }
    
    const astRenderer = new window.ASTTreeRenderer(astOutput);
    
    if (viewMode === 'text') {
      // Renderizar como texto formatado com highlighting
      const textData = typeof astData === 'string' ? astData : JSON.stringify(astData, null, 2);
      astRenderer.renderTextAST(textData);
    } else {
      // Renderizar como árvore visual (padrão)
      astRenderer.render(astData);
    }
    
    // Atualizar os botões toggle (principal e modal)
    updateASTToggleButton(viewMode);
    updateModalToggleButton(viewMode);
  }
  
  // Atualizar visual do botão toggle
  function updateASTToggleButton(mode) {
    if (!astViewToggle) return;
    
    const icon = astViewToggle.querySelector('.view-icon');
    const label = astViewToggle.querySelector('.view-label');
    
    if (mode === 'text') {
      astViewToggle.setAttribute('data-mode', 'text');
      icon.textContent = '📝';
      label.textContent = 'Texto';
      astViewToggle.title = 'Clique para ver como árvore visual';
    } else {
      astViewToggle.setAttribute('data-mode', 'tree');
      icon.textContent = '📊';
      label.textContent = 'Árvore';
      astViewToggle.title = 'Clique para ver como texto formatado';
    }
  }
  
  // Declaração antecipada da função (será definida depois)
  function updateModalToggleButton(mode) {
    // Será implementada na seção do modal
  }
  
  // Toggle AST view mode
  if (astViewToggle) {
    // Inicializar visual do botão
    updateASTToggleButton(astViewMode);
    
    astViewToggle.addEventListener('click', () => {
      // Alternar modo
      astViewMode = astViewMode === 'tree' ? 'text' : 'tree';
      
      // Salvar preferência
      localStorage.setItem('astViewMode', astViewMode);
      
      // Re-renderizar AST com novo modo
      if (currentAstData) {
        renderAST(currentAstData, astViewMode);
      }
    });
  }

  // Renderizar tabela de símbolos
  function renderSymbolTable(symbolTableData) {
    if (!symbolTableOut) return;
    
    symbolTableOut.innerHTML = '';
    
    if (!symbolTableData || symbolTableData.total_symbols === 0) {
      symbolTableOut.textContent = 'Nenhum símbolo declarado.';
      return;
    }
    
    const container = document.createElement('div');
    container.className = 'symbol-table-container';
    
    // Estatísticas gerais
    const stats = document.createElement('div');
    stats.className = 'symbol-stats';
    stats.innerHTML = `
      <span class="meta">Total: ${symbolTableData.total_symbols} símbolos</span>
      <span class="meta">• ${symbolTableData.variables.length} variáveis</span>
      <span class="meta">• ${symbolTableData.functions.length} funções</span>
      <span class="meta">• ${symbolTableData.classes.length} classes</span>
      ${symbolTableData.total_blocks ? `<span class="meta">• ${symbolTableData.total_blocks} blocos</span>` : ''}
      ${symbolTableData.total_statements ? `<span class="meta">• ${symbolTableData.total_statements} instruções</span>` : ''}
    `;
    container.appendChild(stats);
    
    // Função auxiliar para criar seção
    function createSection(title, items, icon) {
      if (items.length === 0) return null;
      
      const section = document.createElement('div');
      section.className = 'symbol-scope';
      
      const header = document.createElement('div');
      header.className = 'symbol-scope-header';
      header.innerHTML = `<strong>${icon} ${title}</strong> <span class="meta">(${items.length})</span>`;
      section.appendChild(header);
      
      const table = document.createElement('table');
      table.className = 'symbol-table';
      
      const thead = document.createElement('thead');
      thead.innerHTML = '<tr><th>Nome</th><th>Tipo</th><th>Detalhes</th></tr>';
      table.appendChild(thead);
      
      const tbody = document.createElement('tbody');
      
      items.forEach(symbol => {
        const row = document.createElement('tr');
        
        const nameCell = document.createElement('td');
        nameCell.className = 'symbol-name';
        nameCell.textContent = symbol.name;
        
        const typeCell = document.createElement('td');
        typeCell.className = 'symbol-type';
        
        let typeIcon = '📦';
        if (symbol.is_function) typeIcon = '🔧';
        else if (symbol.is_class) typeIcon = '🏛️';
        else if (symbol.is_array) typeIcon = '📚';
        else if (symbol.type === 'c_channel') typeIcon = '📡';
        
        typeCell.innerHTML = `${typeIcon} <span>${symbol.type}</span>`;
        
        const detailsCell = document.createElement('td');
        detailsCell.className = 'symbol-details';
        
        const details = [];
        if (symbol.is_array && symbol.array_size) {
          details.push(`array[${symbol.array_size}]`);
        }
        if (symbol.is_function && symbol.return_type) {
          details.push(`→ ${symbol.return_type}`);
          if (symbol.parameters && symbol.parameters.length > 0) {
            const params = symbol.parameters.map(p => `${p.type} ${p.name}`).join(', ');
            details.push(`(${params})`);
          }
        }
        if (symbol.value !== null && symbol.value !== 'None') {
          details.push(`= ${symbol.value}`);
        }
        
        detailsCell.textContent = details.join(' ');
        
        row.appendChild(nameCell);
        row.appendChild(typeCell);
        row.appendChild(detailsCell);
        tbody.appendChild(row);
      });
      
      table.appendChild(tbody);
      section.appendChild(table);
      return section;
    }
    
    // Adicionar seções
    const variablesSection = createSection('Variáveis', symbolTableData.variables, '📦');
    if (variablesSection) container.appendChild(variablesSection);
    
    const functionsSection = createSection('Funções', symbolTableData.functions, '🔧');
    if (functionsSection) container.appendChild(functionsSection);
    
    const classesSection = createSection('Classes', symbolTableData.classes, '🏛️');
    if (classesSection) container.appendChild(classesSection);
    
    // Seção de Blocos (SEQ, PAR)
    if (symbolTableData.blocks && symbolTableData.blocks.length > 0) {
      const blocksSection = document.createElement('div');
      blocksSection.className = 'symbol-scope';
      blocksSection.innerHTML = `
        <div class="symbol-scope-header">
          <strong>🔷 Blocos</strong> <span class="meta">(${symbolTableData.blocks.length})</span>
        </div>
        <div class="block-stats">
          ${Object.entries(symbolTableData.blocks.reduce((acc, b) => {
            acc[b.type] = (acc[b.type] || 0) + 1;
            return acc;
          }, {})).map(([type, count]) => `<span class="meta">${type}: ${count}x</span>`).join(' • ')}
        </div>
      `;
      container.appendChild(blocksSection);
    }
    
    // Seção de Instruções (PRINT, IF, FOR, etc)
    if (symbolTableData.statements && symbolTableData.statements.length > 0) {
      const statementsSection = document.createElement('div');
      statementsSection.className = 'symbol-scope';
      statementsSection.innerHTML = `
        <div class="symbol-scope-header">
          <strong>📝 Instruções</strong> <span class="meta">(${symbolTableData.statements.length})</span>
        </div>
        <div class="statement-stats">
          ${Object.entries(symbolTableData.statements.reduce((acc, s) => {
            acc[s.type] = (acc[s.type] || 0) + 1;
            return acc;
          }, {})).map(([type, count]) => `<span class="meta">${type}: ${count}x</span>`).join(' • ')}
        </div>
      `;
      container.appendChild(statementsSection);
    }
    
    symbolTableOut.appendChild(container);
  }

  // ===== WebSocket Setup =====
  let wsClient = null;
  const wsStatusEl = document.getElementById('wsStatus');
  const wsTextEl = wsStatusEl ? wsStatusEl.querySelector('.ws-text') : null;
  
  function updateWSStatus(status, text) {
    if (!wsStatusEl || !wsTextEl) return;
    wsStatusEl.className = 'ws-status ' + status;
    wsTextEl.textContent = text;
  }
  
  // Inicializar WebSocket Client
  if (window.MiniParWebSocketClient) {
    wsClient = new window.MiniParWebSocketClient('ws://localhost:8001');
    
    // Handlers de eventos
    wsClient.onMessage((data) => {
      if (data.status === 'processing') {
        updateWSStatus('executing', 'Processando...');
      } else if (data.status === 'executing') {
        updateWSStatus('executing', 'Executando...');
      } else if (data.success !== undefined) {
        // Resultado final
        updateWSStatus('connected', 'Conectado');
        processInterpretResult(data);
      }
    });
    
    wsClient.onStatus((status, message) => {
      if (status === 'connected') {
        updateWSStatus('connected', 'Conectado');
      } else if (status === 'disconnected') {
        updateWSStatus('disconnected', 'Desconectado');
      } else if (status === 'reconnecting') {
        updateWSStatus('connecting', 'Reconectando...');
      }
    });
    
    wsClient.onError((error) => {
      console.error('WebSocket error:', error);
      updateWSStatus('disconnected', 'Erro de conexão');
    });
    
    // Conectar
    wsClient.connect().then(() => {
      updateWSStatus('connected', 'Conectado');
    }).catch(() => {
      updateWSStatus('disconnected', 'Desconectado');
    });
  }
  
  // Função auxiliar para processar resultado (usada tanto por WS quanto REST)
  function processInterpretResult(data) {
    if(data.erro){ 
      execOut.textContent=''; 
      lexOut.textContent='❌ '+data.erro; 
      semOut.textContent=''; 
      return; 
    }
    
    // tokens
    let lexText = '';
    if(Array.isArray(data.lexico)){
      lexText = data.lexico.map(t => (typeof t === 'string' ? t : (t.type||t.t||'') + ' ' + (t.lexeme||t.v||t.value||''))).join('\n');
    } else if(typeof data.lexico === 'string') lexText = data.lexico;
    lexOut.textContent = lexText || 'Nenhum token.';
    
    // semantico
    semOut.textContent = data.semantico ? (typeof data.semantico === 'string' ? data.semantico : JSON.stringify(data.semantico,null,2)) : 'Nenhuma análise semântica.';
    
    // ast - renderizar com suporte a toggle tree/text
    // Preferir ast_json (formato objeto) para renderização gráfica, fallback para ast (texto)
    const astData = data.ast_json || data.ast;
    renderAST(astData);
    
    // symbol table
    if (symbolTableOut && data.symbol_table) {
      renderSymbolTable(data.symbol_table);
    } else if (symbolTableOut) {
      symbolTableOut.textContent = 'Tabela de símbolos não disponível.';
    }
    
    // tac
    if(tacOut){
      const tacText = data.tac || data.tac_code || data.threeAddress || data.three_address || data.three_address_code || '';
      tacOut.textContent = tacText ? (typeof tacText === 'string' ? tacText : JSON.stringify(tacText,null,2)) : 'TAC não fornecido pelo backend.';
    }
    
    // exec
    const execText = data.saida || data.exec || data.execucao || data.stdout || data.output || '';
    execOut.textContent = (typeof execText === 'string' ? execText : JSON.stringify(execText,null,2)) || '(Nenhuma saída de execução fornecida pelo backend)';
    
    // input interativo
    if(data.waiting_for_input){
      currentRunId = data.run_id || data.runId || null;
      showInputPrompt(currentRunId, data.prompt || '');
    } else {
      removeInputPrompt();
      currentRunId = null;
    }
  }

  // Executar -> enviar para backend (usa WebSocket se disponível, senão REST)
  async function interpretarCodigo(){
    const code = getEditorValue();
    execOut.textContent = '🔄 Executando...';
    lexOut.textContent = '🔄 Processando...'; 
    semOut.textContent = '🔄 Processando...';
    document.getElementById('astOutput').textContent = '🔄 Gerando árvore...';
    if (symbolTableOut) symbolTableOut.textContent = '🔄 Processando...';
    
    // WebSocket desabilitado - usar REST API para suporte a input interativo
    // if (wsClient && wsClient.isConnected()) {
    //   try {
    //     updateWSStatus('executing', 'Executando...');
    //     wsClient.send(code);
    //     return;
    //   } catch (err) {
    //     console.error('WebSocket error, falling back to REST:', err);
    //   }
    // }
    
    // Fallback para REST API
    try{
      const resp = await fetch('http://127.0.0.1:8000/interpretar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})});
      const data = await resp.json();
      processInterpretResult(data);
    }catch(err){ 
      console.error(err); 
      execOut.textContent=''; 
      lexOut.textContent='❌ Erro ao conectar com o servidor.'; 
      semOut.textContent=''; 
      document.getElementById('astOutput').textContent=''; 
    }
  }

  runBtn.addEventListener('click', interpretarCodigo);
  
  // Atalho CTRL+ENTER para executar código
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      interpretarCodigo();
    }
  });
  
  // Inicializar CodeMirror (se disponível) e definir conteúdo inicial + tema
  if(window.CodeMirror){
    // Criar instância do editor e expor para outros helpers
    window.editorInstance = CodeMirror.fromTextArea(codeEl, {lineNumbers:true, mode:'text/x-csrc', theme:'dracula', indentUnit:2, autofocus:true});
    // Esconder o gutter antigo (usamos numeração de linhas do CodeMirror)
    if(gutter) gutter.style.display = 'none';
    // Quando conteúdo do CodeMirror muda, atualizar saídas como gutter de contagem de tokens
    window.editorInstance.on('change', ()=>{ updateGutter(); });
  }
  // Definir conteúdo inicial
  setEditorValue(sample); updateGutter();
  // Aplicar tema inicial de acordo com seletor
  applyTheme(themeSel && themeSel.value ? themeSel.value : 'dark');

  // Handlers de toggle para colapsar/expandir painéis (restaurar funcionalidade)
  document.querySelectorAll('.toggle').forEach(btn=>{
    btn.addEventListener('click', (e)=>{
      const panel = btn.closest('.panel');
      if(!panel) return;
      const collapsed = panel.classList.toggle('collapsed');
      btn.textContent = collapsed ? '▸' : '▾';
      const out = panel.querySelector('.output');
      if(out) out.setAttribute('aria-hidden', collapsed ? 'true' : 'false');
    });
  });

  // Garantir que painéis do lado direito estejam visíveis no carregamento (corrige casos onde
  // painéis ficaram colapsados ou toggles ficaram dessincronizados)
  (function restoreRightPanels(){
    const panels = document.querySelectorAll('aside.right .panel');
    panels.forEach(p => {
      p.classList.remove('collapsed');
      const out = p.querySelector('.output');
      if(out) out.setAttribute('aria-hidden', 'false');
      const toggle = p.querySelector('.toggle');
      if(toggle) toggle.textContent = '▾';
    });
  })();

  // Forçar garantia de que coluna direita e conteúdo dos painéis estejam visíveis (cobre casos
  // onde CSS ou JS anterior acidentalmente definiu display:none). Isso é seguro e sem efeito
  // se os elementos já estiverem visíveis
  const rightCol = document.querySelector('aside.right');
  if(rightCol){
    rightCol.style.display = rightCol.style.display || 'flex';
    rightCol.style.flexDirection = rightCol.style.flexDirection || 'column';
  }
  document.querySelectorAll('aside.right .panel').forEach(p => {
    p.style.display = p.style.display || 'block';
    const out = p.querySelector('.output');
    if(out){ out.style.display = out.style.display || 'block'; out.style.visibility = 'visible'; }
  });

  // Helpers de UI de entrada para programas interativos
  function showInputPrompt(runId, promptText){
    // Criar uma pequena área de entrada dentro de execOut
    removeInputPrompt();
    const wrapper = document.createElement('div');
    wrapper.className = 'exec-input-wrapper';
    wrapper.style.display = 'flex';
    wrapper.style.gap = '8px';
    wrapper.style.marginTop = '8px';

    const label = document.createElement('div');
    label.textContent = promptText || 'Entrada requerida:';
    label.className = 'meta';
    label.style.alignSelf = 'center';

    const input = document.createElement('input');
    input.type = 'text';
    input.className = 'exec-input';
    input.style.flex = '1';
    input.style.padding = '8px';
    input.placeholder = 'Digite a entrada e pressione Enviar';

    const btn = document.createElement('button');
    btn.className = 'btn primary';
    btn.textContent = 'Enviar';
    btn.addEventListener('click', ()=>{
      const val = input.value || '';
      sendRunInput(runId, val);
    });

    wrapper.appendChild(label);
    wrapper.appendChild(input);
    wrapper.appendChild(btn);

    execOut.appendChild(wrapper);
    // Focar no input
    setTimeout(()=>input.focus(),50);
  }

  function removeInputPrompt(){
    const existing = execOut.querySelector('.exec-input-wrapper');
    if(existing) existing.remove();
  }

  async function sendRunInput(runId, value){
    if(!runId) return;
    try{
      const resp = await fetch('http://127.0.0.1:8000/interpretar/input',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({run_id: runId, input: value})});
      const data = await resp.json();
      // Atualizar saída de execução e estado de espera
      execOut.textContent = data.exec || data.stdout || execOut.textContent;
      if(data.waiting_for_input){
        showInputPrompt(runId, data.prompt || 'Entrada:');
      } else {
        removeInputPrompt();
        currentRunId = null;
      }
    }catch(err){ console.error('Erro enviando input', err); }
  }

  // Sem painel de entrada externo: usar prompt exec inline (showInputPrompt) para entrada interativa

  // ==========================================================================
  // MODAL DE AST AMPLIADA
  // ==========================================================================
  
  const astModal = document.getElementById('astModal');
  const astModalContent = document.getElementById('astModalContent');
  const astExpandBtn = document.getElementById('astExpandBtn');
  const astModalClose = document.getElementById('astModalClose');
  const astViewToggleModal = document.getElementById('astViewToggleModal');
  
  // Abrir modal
  if (astExpandBtn) {
    astExpandBtn.addEventListener('click', () => {
      if (currentAstData) {
        astModal.classList.add('show');
        // Copiar conteúdo da AST para o modal
        renderASTInModal(currentAstData, astViewMode);
      } else {
        astModalContent.textContent = 'AST ainda não gerada. Execute um código primeiro.';
        astModal.classList.add('show');
      }
    });
  }
  
  // Fechar modal
  if (astModalClose) {
    astModalClose.addEventListener('click', () => {
      astModal.classList.remove('show');
    });
  }
  
  // Fechar modal ao clicar fora do conteúdo
  if (astModal) {
    astModal.addEventListener('click', (e) => {
      if (e.target === astModal) {
        astModal.classList.remove('show');
      }
    });
  }
  
  // Fechar modal com ESC
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && astModal.classList.contains('show')) {
      astModal.classList.remove('show');
    }
  });
  
  // Toggle de visualização no modal
  if (astViewToggleModal) {
    astViewToggleModal.addEventListener('click', () => {
      // Alternar modo
      const newMode = astViewMode === 'tree' ? 'text' : 'tree';
      astViewMode = newMode;
      
      // Salvar preferência
      localStorage.setItem('astViewMode', astViewMode);
      
      // Re-renderizar AST no modal e na tela principal
      if (currentAstData) {
        renderASTInModal(currentAstData, astViewMode);
        renderAST(currentAstData, astViewMode);
      }
    });
  }
  
  // Atualizar botão do modal (sobrescrever a função stub)
  updateModalToggleButton = function(mode) {
    if (!astViewToggleModal) return;
    
    const icon = astViewToggleModal.querySelector('.view-icon');
    const label = astViewToggleModal.querySelector('.view-label');
    
    if (mode === 'text') {
      astViewToggleModal.setAttribute('data-mode', 'text');
      icon.textContent = '�';
      label.textContent = 'Texto';
      astViewToggleModal.title = 'Clique para ver como árvore visual';
    } else {
      astViewToggleModal.setAttribute('data-mode', 'tree');
      icon.textContent = '📊';
      label.textContent = 'Árvore';
      astViewToggleModal.title = 'Clique para ver como texto formatado';
    }
  };
  
  // Renderizar AST no modal
  function renderASTInModal(astData, mode) {
    if (!astModalContent) return;
    
    updateModalToggleButton(mode);
    astModalContent.innerHTML = '';
    
    if (!astData) {
      astModalContent.textContent = 'AST ainda não gerada.';
      return;
    }
    
    if (mode === 'tree') {
      // Modo árvore visual - usar ast-tree.js
      if (typeof renderASTTree === 'function') {
        try {
          renderASTTree(astData, astModalContent);
        } catch (err) {
          console.error('Erro ao renderizar árvore:', err);
          astModalContent.innerHTML = `<div class="error">Erro ao renderizar árvore visual: ${err.message}</div>`;
        }
      } else {
        astModalContent.textContent = 'Renderizador de árvore não disponível.';
      }
    } else {
      // Modo texto - mostrar AST formatado
      if (typeof astData === 'string') {
        astModalContent.textContent = astData;
      } else {
        astModalContent.textContent = JSON.stringify(astData, null, 2);
      }
      
      // Aplicar syntax highlighting
      if (astModalContent.textContent) {
        astModalContent.innerHTML = syntaxHighlightAST(astModalContent.textContent);
      }
    }
  }

});