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
  const tokCount = document.getElementById('tokCount');
  const status = document.getElementById('status');
  const exportBtn = document.getElementById('exportBtn');
  const themeSel = document.getElementById('themeSel');
  let currentRunId = null;

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
    'Print & Arithmetic': `SEQ {
    print("Soma: " + (1 + 2) + "\\n");
    print("Mult: " + (2 * 3) + "\\n");
}
`,
    'Variables & If': `SEQ {
    INT x;
    INT y;
    x = 10;
    y = 5;
    if (x > y) {
        print("x maior\\n");
    } else {
        print("x menor\\n");
    }
}
`,
    'Loops & Functions': `SEQ {
    INT soma(INT a, INT b) {
        return a + b;
    }
    
    INT i;
    for i = 0; i < 3; i = i + 1 {
        print("i=" + i + "\\n");
    }
    print("soma 3+4 = " + soma(3,4) + "\\n");
}
`,
    'Channels Send/Receive': `# Comunicação por canais
SEQ {
    C_CHANNEL canal_resultados;
    canal_resultados.send(42);
    print("Enviado 42\\n");
}
`,
    'Hello World (threads)': `SEQ {
    VOID f1() {
        INT i;
        i = 0;
        while (i != 3) {
            print("A:" + i + "\\n");
            i = i + 1;
        }
    }
    
    VOID f2() {
        INT j;
        j = 3;
        while (j != 0) {
            print("B:" + j + "\\n");
            j = j - 1;
        }
    }
    
    PAR {
        f1();
        f2();
    }
}
`,
    'Threads - cliente/servidor (programa2)': `# Demo simplificado cliente/servidor
SEQ {
    C_CHANNEL canal_resultados;
    canal_resultados.send(10);
    print("Enviado 10 para canal\\n");
}
`
  };

  // Carregar exemplo
  sampleBtn.addEventListener('click', ()=>{
    const sel = document.getElementById('exampleSel');
    if(sel && sel.value && examples[sel.value]){ setEditorValue(examples[sel.value]); status.textContent = `Exemplo: ${sel.value} carregado`; }
    else { setEditorValue(sample); status.textContent = 'Exemplo carregado'; }
    updateGutter(); setTimeout(()=>status.textContent='Pronto',800);
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

  // Executar -> enviar para backend
  async function interpretarCodigo(){
    const code = getEditorValue();
    execOut.textContent = '🔄 Executando...';
    lexOut.textContent = '🔄 Processando...'; semOut.textContent = '🔄 Processando...';
    try{
      const resp = await fetch('http://127.0.0.1:8000/interpretar',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code})});
      const data = await resp.json();
      if(data.erro){ execOut.textContent=''; lexOut.textContent='❌ '+data.erro; semOut.textContent=''; return; }
      // tokens
      let lexText = '';
      if(Array.isArray(data.lexico)){
        lexText = data.lexico.map(t => (typeof t === 'string' ? t : (t.type||t.t||'') + ' ' + (t.lexeme||t.v||t.value||''))).join('\n');
      } else if(typeof data.lexico === 'string') lexText = data.lexico;
      lexOut.textContent = lexText || 'Nenhum token.';
      // semantico
      semOut.textContent = data.semantico ? (typeof data.semantico === 'string' ? data.semantico : JSON.stringify(data.semantico,null,2)) : 'Nenhuma análise semântica.';
      // ast
      document.getElementById('astOutput').textContent = data.ast || 'Nenhuma árvore sintática gerada.';
      // tac (código de 3 endereços) — backend pode fornecer com chaves diferentes
      if(tacOut){
        const tacText = data.tac || data.tac_code || data.threeAddress || data.three_address || data.three_address_code || '';
        tacOut.textContent = tacText ? (typeof tacText === 'string' ? tacText : JSON.stringify(tacText,null,2)) : 'TAC não fornecido pelo backend.';
      }
      // exec
      const execText = data.exec || data.execucao || data.stdout || data.output || '';
      execOut.textContent = (typeof execText === 'string' ? execText : JSON.stringify(execText,null,2)) || '(Nenhuma saída de execução fornecida pelo backend)';
      // Tratamento de entrada interativa: se backend indica que está esperando entrada, mostrar prompt
      if(data.waiting_for_input){
        currentRunId = data.run_id || data.runId || null;
        showInputPrompt(currentRunId, data.prompt || '');
      } else {
        removeInputPrompt();
        currentRunId = null;
      }
    }catch(err){ console.error(err); execOut.textContent=''; lexOut.textContent='❌ Erro ao conectar com o servidor.'; semOut.textContent=''; document.getElementById('astOutput').textContent=''; }
  }

  runBtn.addEventListener('click', interpretarCodigo);
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
});