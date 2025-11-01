document.addEventListener("DOMContentLoaded", () => {
// Editor helpers
    const codeEl = document.getElementById('code');
    const gutter = document.getElementById('gutter');
    const runBtn = document.getElementById('runBtn');
    const clearBtn = document.getElementById('clearBtn');
    const sampleBtn = document.getElementById('sampleBtn');
    const lexOut = document.getElementById('lexOutput');
    const semOut = document.getElementById('semOutput');
    const tokCount = document.getElementById('tokCount');
    const status = document.getElementById('status');
    const exportBtn = document.getElementById('exportBtn');
    const themeSel = document.getElementById('themeSel');

    // Update line numbers
    function updateGutter(){
      const lines = codeEl.value.split('\n').length || 1;
      let s='';
      for(let i=1;i<=lines;i++) s += i + '\n';
      gutter.textContent = s;
    }
    codeEl.addEventListener('input', updateGutter);
    codeEl.addEventListener('scroll', () => { gutter.scrollTop = codeEl.scrollTop });

    // Shortcuts
    window.addEventListener('keydown', (e)=>{
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter'){
        e.preventDefault(); run();
      }
    })

    // Simple sample code
    const sample = `// Exemplo MiniPar-like\nvar x = 10;\nvar s = "olá";\nif (x > 5) {\n  x = x + 1;\n}\nprint(x);\nprint(s);\nlet y = x + z; // z não declarado (semântica)\n`;

    sampleBtn.addEventListener('click', ()=>{ codeEl.value = sample; updateGutter(); status.textContent = 'Exemplo carregado'; setTimeout(()=>status.textContent='Pronto',800)});
    clearBtn.addEventListener('click', ()=>{ codeEl.value=''; updateGutter(); lexOut.textContent=''; semOut.textContent=''; tokCount.textContent='0'; status.textContent='Limpo'; setTimeout(()=>status.textContent='Pronto',600)});

    // Theme toggle (very simple)
    themeSel.addEventListener('change', (e)=>{
      if(e.target.value === 'light'){
        document.documentElement.style.setProperty('--bg','#f5f7fb');
        document.documentElement.style.setProperty('--muted','#4b5563');
        document.body.style.background = 'linear-gradient(180deg,#f8fafc,#eef2ff)';
        document.querySelectorAll('.card, .panel').forEach(n=>n.style.background='white');
        document.querySelectorAll('.code').forEach(n=>n.style.color='#0b1220');
      } else {
        document.documentElement.style.removeProperty('--bg');
        document.body.style.background = 'linear-gradient(180deg,#071025,#071827)';
        document.querySelectorAll('.card, .panel').forEach(n=>n.style.background='linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01))');
        document.querySelectorAll('.code').forEach(n=>n.style.color='#e6eef6');
      }
    })

   //render
function renderTokens(tokensArray) {
    const lexOut = document.getElementById('lexOutput');
    if (tokensArray.length === 0) {
        lexOut.textContent = 'Nenhum token.';
        return;
    }

    // Constrói string com cada token em uma linha
    const tokenText = tokensArray.map(t => {
        const typeName = t.type.name ? t.type.name : t.type; // caso seu token tenha type.name
        return `Token(${typeName}, '${t.lexeme}', ${t.line})`;
    }).join('\n');

    // Mostra no lexOutput respeitando quebras
    lexOut.textContent = tokenText;

    // Garante estilo tipo terminal
    lexOut.style.whiteSpace = 'pre';
    lexOut.style.fontFamily = 'monospace';
}
    async function interpretarCodigo() {
    // Mostra status temporário
  document.getElementById("lexOutput").textContent = "🔄 Processando...";
  document.getElementById("semOutput").textContent = "🔄 Processando...";
  document.getElementById("astOutput").textContent = "🔄 Processando...";

  try {
    const response = await fetch("http://127.0.0.1:8000/interpretar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo: codeEl.value }), // <- nome correto do campo do FastAPI
    });

    const data = await response.json();

    if (data.erro) {
      document.getElementById("lexOutput").textContent = "❌ Erro: " + data.erro;
      document.getElementById("semOutput").textContent = "";
      document.getElementById("astOutput").textContent = "";
      return;
    }

    // Mostra os resultados recebidos do FastAPI

    console.log("verificando tokens: ",data.tokens);
    // Supondo que data.tokens seja uma string com quebras de linha
    
    const tokens = data.tokens;
   // const tokensArray = tokens.split("\n"); // cada linha vira um elemento do array
  
    document.getElementById("lexOutput").textContent = tokens || "Nenhum token gerado";

    document.getElementById("astOutput").textContent =
      data.ast || "Nenhuma árvore sintática gerada.";

    document.getElementById("semOutput").textContent =
      data.semantico || "Nenhuma análise semântica realizada.";

  } catch (error) {
    console.error("Erro de conexão:", error);
    document.getElementById("lexOutput").textContent =
      "❌ Erro ao conectar com o servidor FastAPI.";
    document.getElementById("semOutput").textContent = "";
    document.getElementById("astOutput").textContent = "";
  }
}


    runBtn.addEventListener('click', interpretarCodigo);

    exportBtn.addEventListener('click', ()=>{
      // copy token JSON to clipboard
      const tokens = lex(codeEl.value);
      navigator.clipboard.writeText(JSON.stringify(tokens, null, 2)).then(()=>{
        status.textContent = 'Tokens copiados'; setTimeout(()=>status.textContent='Pronto',800)
      }).catch(()=>{ status.textContent='Erro ao copiar' })
    })

    // init
    codeEl.value = sample; updateGutter();
  });