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

    // ======== LEXER & SEMANTIC (Front-end demo) ========
    // This lexer is a lightweight demo for front-end visualization only.
    // It recognizes: keywords, identifiers, numbers, strings, operators, punctuation and comments.

    const KEYWORDS = new Set(['var','let','if','else','while','for','return','func','print']);
    const tokenPatterns = [
      ['WHITESPACE', /^\s+/],
      ['COMMENT', /^\/\/.*/],
      ['STRING', /^"([^"\\]|\\.)*"/],
      ['NUMBER', /^\d+(?:\.\d+)?/],
      ['IDENT', /^[A-Za-z_][A-Za-z0-9_]*/],
      ['OP', /^==|!=|<=|>=|=>|\+|\-|\*|\/|=|<|>/],
      ['PUNC', /^[\(\)\{\}\[\];,\.]/],
    ];

    function lex(input){
      let i=0; const tokens=[];
      while(i < input.length){
        const slice = input.slice(i);
        let matched=false;
        for(const [type, pat] of tokenPatterns){
          const m = slice.match(pat);
          if(m){
            matched=true; const txt = m[0];
            if(type === 'WHITESPACE'){
              // skip but keep newlines for position
              i += txt.length; break;
            }
            if(type === 'COMMENT'){
              tokens.push({type:'COMMENT', value:txt}); i+=txt.length; break;
            }
            if(type === 'IDENT'){
              const kind = KEYWORDS.has(txt) ? 'KEYWORD' : 'IDENT';
              tokens.push({type:kind, value:txt}); i+=txt.length; break;
            }
            tokens.push({type:type, value:txt}); i+=txt.length; break;
          }
        }
        if(!matched){
          // unknown char -> produce an error token and advance 1
          tokens.push({type:'UNKNOWN', value:input[i]}); i++;
        }
      }
      return tokens;
    }

    // Semantic: very simple one-pass symbol table for var/let declarations and use-before-declare
    function semanticCheck(tokens){
      const messages = [];
      const symbols = new Map(); // name -> {declared:true, lastValueType: 'number'|'string'|null}

      // helper to peek next non-comment/whitespace token
      function nextNonComment(idx){
        let j = idx+1; while(j < tokens.length && (tokens[j].type === 'COMMENT')) j++; return tokens[j] || null;
      }

      for(let i=0;i<tokens.length;i++){
        const t = tokens[i];
        if(t.type === 'KEYWORD' && (t.value === 'var' || t.value === 'let')){
          // expect identifier next
          const nx = nextNonComment(i);
          if(nx && nx.type === 'IDENT'){
            const name = nx.value;
            if(symbols.has(name)){
              messages.push({kind:'warn', text:`Variável '${name}' já declarada.`});
            } else {
              symbols.set(name, {declared:true, type:null});
              messages.push({kind:'info', text:`Declarada '${name}'`});
            }
          } else {
            messages.push({kind:'err', text:`Esperado identificador após '${t.value}'.`});
          }
        }
        if(t.type === 'IDENT'){
          // detect usage like IDENT ( ... or IDENT = ... ) — naive
          const nx = nextNonComment(i);
          if(nx && nx.type === 'OP' && nx.value === '='){
            // assignment, try to detect literal type on right
            // scan ahead for next token that is NUMBER or STRING or IDENT
            let j=i+1; let found=null;
            while(j<tokens.length){ if(tokens[j].type==='NUMBER'||tokens[j].type==='STRING'||tokens[j].type==='IDENT'){ found=tokens[j]; break; } j++; }
            if(found){
              if(!symbols.has(t.value)){
                messages.push({kind:'err', text:`Atribuição a variável não declarada '${t.value}'.`});
              } else {
                const st = symbols.get(t.value);
                const newType = found.type==='NUMBER'? 'number' : (found.type==='STRING'? 'string' : 'ident');
                if(st.type && st.type !== newType && newType !== 'ident'){
                  messages.push({kind:'warn', text:`Possível mudança de tipo em '${t.value}' de ${st.type} para ${newType}.`});
                }
                if(newType !== 'ident') st.type = newType;
                symbols.set(t.value, st);
              }
            }
          } else {
            // usage context - check declared
            // avoid counting declarations (handled above)
            // if previous token was keyword var/let ignore
            const prev = tokens[i-1];
            if(!(prev && prev.type==='KEYWORD' && (prev.value==='var' || prev.value==='let'))){
              if(!symbols.has(t.value)){
                messages.push({kind:'err', text:`Uso de variável não declarada '${t.value}'.`});
              }
            }
          }
        }
        if(t.type === 'UNKNOWN'){
          messages.push({kind:'err', text:`Caractere desconhecido: '${t.value}'`});
        }
      }

      return {messages, symbols};
    }

    // Render tokens to the lexOutput area
    function renderTokens(tokens){
      tokCount.textContent = tokens.length;
      if(tokens.length === 0){ lexOut.textContent = 'Nenhum token.'; return; }
      // Build HTML list
      const container = document.createElement('div');
      container.className = 'tokens';
      tokens.forEach((tk, idx)=>{
        const row = document.createElement('div'); row.className = 'token-row';
        const idxEl = document.createElement('div'); idxEl.className='chip'; idxEl.textContent = idx+1;
        const typeEl = document.createElement('div'); typeEl.className='chip'; typeEl.textContent = tk.type;
        const valEl = document.createElement('div'); valEl.textContent = tk.value; valEl.style.fontFamily='var(--mono)';
        // color by type
        if(tk.type === 'KEYWORD') valEl.className='tok-keyword';
        if(tk.type === 'IDENT') valEl.className='tok-ident';
        if(tk.type === 'NUMBER') valEl.className='tok-number';
        if(tk.type === 'STRING') valEl.className='tok-string';
        if(tk.type === 'OP') valEl.className='tok-operator';
        if(tk.type === 'UNKNOWN') valEl.className='err';

        row.appendChild(idxEl); row.appendChild(typeEl); row.appendChild(valEl);
        container.appendChild(row);
      });
      lexOut.innerHTML = '';
      lexOut.appendChild(container);
    }

    function renderSemantic(res){
      semOut.innerHTML = '';
      if(res.messages.length === 0){ semOut.textContent = 'Sem problemas aparentes.'; return; }
      const ul = document.createElement('div'); ul.style.display='flex'; ul.style.flexDirection='column'; ul.style.gap='8px';
      res.messages.forEach(m =>{
        const el = document.createElement('div');
        el.textContent = (m.kind==='err'? 'Erro: ' : (m.kind==='warn'? 'Aviso: ' : 'Info: ')) + m.text;
        el.className = m.kind==='err'? 'err' : (m.kind==='warn'? 'meta' : '');
        ul.appendChild(el);
      });
      semOut.appendChild(ul);
    }

    // Run pipeline
    function run(){
      const src = codeEl.value;
      if(!src.trim()){ status.textContent = 'Editor vazio'; return; }
      status.textContent = 'Analisando...';
      try{
        const tokens = lex(src);
        renderTokens(tokens);
        const sem = semanticCheck(tokens);
        renderSemantic(sem);
        document.getElementById('astOutput').textContent = 'Geração de AST ainda não implementada.';
        status.textContent = 'Concluído';
      }catch(err){
        status.textContent = 'Erro';
        lexOut.textContent = '';
        semOut.textContent = 'Erro ao executar análise: ' + err.message;
        console.error(err);
      }
      setTimeout(()=>status.textContent='Pronto', 600);
    }

    runBtn.addEventListener('click', run);

    exportBtn.addEventListener('click', ()=>{
      // copy token JSON to clipboard
      const tokens = lex(codeEl.value);
      navigator.clipboard.writeText(JSON.stringify(tokens, null, 2)).then(()=>{
        status.textContent = 'Tokens copiados'; setTimeout(()=>status.textContent='Pronto',800)
      }).catch(()=>{ status.textContent='Erro ao copiar' })
    })

    // init
    codeEl.value = sample; updateGutter();