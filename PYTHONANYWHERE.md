# 🐍 Deploy no PythonAnywhere - Guia Completo

## 📋 Sobre PythonAnywhere

- ✅ **100% Grátis** (plano básico)
- ✅ Muito fácil de configurar
- ✅ Não precisa cartão de crédito
- ⚠️ WebSocket só em plano pago ($5/mês)
- ✅ Perfeito para projetos acadêmicos

## 🚀 Deploy em 10 Minutos

### Passo 1: Preparar Arquivo Local

No seu computador:

```bash
cd /home/marco/ufal/minipar-interpreter-POO
./prepare_pythonanywhere.sh
```

Isso cria `minipar-pythonanywhere.tar.gz` (~124 KB)

### Passo 2: Criar Conta PythonAnywhere

1. Acesse: https://www.pythonanywhere.com
2. Clique em **Pricing & signup**
3. Escolha **Create a Beginner account** (grátis)
4. Preencha:
   - Username (ex: `minipar2025`)
   - Email
   - Password
5. Confirme email

### Passo 3: Upload do Arquivo

1. No dashboard, clique em **Files**
2. Clique no botão **Upload a file**
3. Selecione `minipar-pythonanywhere.tar.gz`
4. Aguarde upload (30 segundos)

### Passo 4: Descompactar e Instalar

1. No dashboard, clique em **Consoles**
2. Clique em **Bash** (abre novo console)
3. No console bash, execute:

```bash
# Criar diretório e descompactar
mkdir -p minipar-interpreter
tar -xzf minipar-pythonanywhere.tar.gz -C minipar-interpreter
cd minipar-interpreter

# Criar ambiente virtual com Python 3.10 (importante!)
python3.10 -m venv venv
source venv/bin/activate

# Verificar versão (deve mostrar 3.10)
python --version

# Instalar dependências
pip install --upgrade pip
pip install -r requirements.txt
```

Aguarde instalação (~2 minutos)

### Passo 5: Criar Web App

1. Volte ao dashboard
2. Clique na aba **Web**
3. Clique em **Add a new web app**
4. Clique **Next** (aceita domínio gratuito)
5. Escolha **Manual configuration** (NÃO escolha framework)
6. Python version: **3.10**
7. Clique **Next**

### Passo 6: Configurar Web App

Na página de configuração da Web App:

#### 6.1 - Virtualenv

⚠️ **IMPORTANTE**: O venv criado pode ter Python 3.13, mas o web app precisa de 3.10.

**Solução**: Recriar o virtualenv com Python 3.10:

No Bash console:
```bash
cd ~/minipar-interpreter
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Depois, na página de configuração da Web App:

Seção **Virtualenv**:
1. Clique em **Enter path to a virtualenv**
2. Digite: `/home/SEU_USERNAME/minipar-interpreter/venv`
3. Clique no ✓ (checkmark)
4. Verifique que aparece: **Python version: 3.10**

#### 6.2 - WSGI Configuration File

Seção **Code**:
1. Clique no link do arquivo WSGI (ex: `/var/www/minipar2025_pythonanywhere_com_wsgi.py`)
2. **DELETE TODO O CONTEÚDO** do arquivo
3. Abra o arquivo `pythonanywhere_wsgi.py` no seu computador
4. **Copie todo o conteúdo**
5. **Cole** no editor do PythonAnywhere
6. **IMPORTANTE**: Na linha 12, mude:
   ```python
   USERNAME = 'seu_username'  # ⚠️ MUDE AQUI!
   ```
   Para:
   ```python
   USERNAME = 'minipar2025'  # Seu username real
   ```
7. Clique em **Save** (canto superior direito)

#### 6.3 - Static Files (Opcional mas recomendado)

Seção **Static files**:

Clique em **Enter URL** e **Enter path**:

| URL | Directory |
|-----|-----------|
| `/static/` | `/home/SEU_USERNAME/minipar-interpreter/frontend` |

### Passo 7: Reload & Testar

1. Volte para a aba **Web**
2. No topo, clique no botão verde **Reload SEU_USERNAME.pythonanywhere.com**
3. Aguarde reload (~10 segundos)
4. Clique no link: `http://seu_username.pythonanywhere.com`

### Passo 8: Testar Funcionalidade

No seu navegador:
```
http://seu_username.pythonanywhere.com
```

Teste:
1. ✅ Página carrega
2. ✅ Selecionar exemplo "Hello World"
3. ✅ Clicar "Executar"
4. ✅ Ver resultado em "Saída: EXECUÇÃO"

## 🔧 Troubleshooting

### ⚠️ Erro: "Wrong Python version (3.13 instead of 3.10)"

**Causa**: O virtualenv foi criado com Python 3.13 (padrão), mas o web app está configurado para 3.10

**Solução Rápida**:
```bash
# No Bash console
cd ~/minipar-interpreter
rm -rf venv
python3.10 -m venv venv
source venv/bin/activate
python --version  # Deve mostrar: Python 3.10.x
pip install --upgrade pip
pip install -r requirements.txt
```

Depois: Web → **Reload**

**Alternativa**: Mudar web app para Python 3.13
1. Web → Python version: 3.13
2. Recriar venv com `python3.13 -m venv venv`
3. Reinstalar dependências
4. Reload

### Erro 404 - Page Not Found

**Causa**: WSGI não configurado corretamente

**Solução**:
1. Web → WSGI configuration file
2. Verificar que USERNAME está correto
3. Save e Reload

### Erro 502 - Bad Gateway

**Causa**: Erro no código WSGI ou dependências faltando

**Solução**:
1. Web → Error log (ler últimas linhas)
2. Verificar virtualenv path
3. Reinstalar dependências:
```bash
cd ~/minipar-interpreter
source venv/bin/activate
pip install -r requirements.txt
```

### Erro "Module not found"

**Causa**: Dependência não instalada

**Solução**:
```bash
cd ~/minipar-interpreter
source venv/bin/activate
pip install [nome-do-modulo]
```

### Página em branco

**Causa**: Frontend não está sendo servido

**Solução**:
1. Verificar Static files configurado
2. Ou editar WSGI para servir frontend corretamente
3. Reload

### Código não executa

**Causa**: API /interpretar não está funcionando

**Solução**:
1. Abrir console do navegador (F12)
2. Ver erro JavaScript
3. Verificar que URL da API está correta
4. Web → Error log

## 📊 Logs

### Ver Erro Log

1. Web → Error log
2. Ver últimas 100 linhas

### Ver Server Log

1. Web → Server log
2. Mostra requisições HTTP

### Ver Access Log

1. Web → Access log
2. Mostra acessos ao site

## 🔄 Atualizar Código

### Método 1: Upload Completo (Recomendado)

Quando fizer mudanças no código:

**1. No seu computador local:**
```bash
cd /home/marco/ufal/minipar-interpreter-POO

# Gerar novo arquivo com as mudanças
./prepare_pythonanywhere.sh

# Isso cria minipar-pythonanywhere.tar.gz atualizado
```

**2. No PythonAnywhere:**

a) **Upload do novo arquivo:**
   - Dashboard → **Files**
   - Clique em **Upload a file**
   - Selecione o novo `minipar-pythonanywhere.tar.gz`
   - Confirme substituição

b) **No Bash console:**
```bash
# Backup da versão antiga (opcional)
mv minipar-interpreter minipar-interpreter.backup

# Criar novo diretório e descompactar
mkdir -p minipar-interpreter
tar -xzf minipar-pythonanywhere.tar.gz -C minipar-interpreter
cd minipar-interpreter

# Recriar ambiente virtual (se houve mudanças em requirements.txt)
python3.10 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

c) **Reload:**
   - Web → Botão verde **"Reload seu_username.pythonanywhere.com"**

**3. Testar:**
   - Acessar `http://seu_username.pythonanywhere.com`
   - Verificar se mudanças aparecem

### Método 2: Atualizar Arquivos Específicos (Rápido)

Para mudanças pequenas em arquivos individuais:

**1. Editar arquivo diretamente no PythonAnywhere:**
   - Files → Browse files
   - Navegar até o arquivo (ex: `minipar-interpreter/frontend/home.js`)
   - Clicar no arquivo para editar
   - Fazer mudanças
   - Save

**2. Ou usar Bash console:**
```bash
cd ~/minipar-interpreter

# Exemplo: atualizar arquivo CSS
nano frontend/home.css
# Editar → CTRL+O (salvar) → CTRL+X (sair)

# Exemplo: atualizar arquivo Python
nano src/lexer/Lexer.py
```

**3. Reload:**
   - Web → **Reload**

### Método 3: Git (Avançado)

Se seu código está no GitHub/GitLab:

**Setup inicial (uma vez):**
```bash
cd ~
git clone https://github.com/TheMarksan/minipar-interpreter-POO.git minipar-interpreter
cd minipar-interpreter
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Para atualizar:**
```bash
cd ~/minipar-interpreter
git pull origin main

# Se requirements.txt mudou:
source venv/bin/activate
pip install -r requirements.txt

# Web → Reload
```

### Método 4: Atualizar apenas Frontend

Se mudou apenas HTML/CSS/JS:

```bash
cd ~/minipar-interpreter/frontend

# Fazer upload dos arquivos específicos via Files
# Ou editar diretamente no editor do PythonAnywhere
```

**Não precisa reload** se for apenas arquivos estáticos!
Apenas limpe cache do navegador: **CTRL+SHIFT+R**

### 🎯 Quando Usar Cada Método:

| Situação | Método Recomendado |
|----------|-------------------|
| **Mudanças grandes** (múltiplos arquivos) | Método 1 (Upload completo) |
| **1-2 arquivos pequenos** | Método 2 (Editar direto) |
| **Desenvolvimento contínuo** | Método 3 (Git) |
| **Apenas CSS/JS/HTML** | Método 4 (Frontend only) |
| **Nova dependência** | Método 1 + reinstalar venv |

### ⚠️ Cuidados:

1. **Sempre faça backup** antes de atualizar:
   ```bash
   cp -r minipar-interpreter minipar-interpreter.backup
   ```

2. **Verifique Error log** após reload:
   - Web → Error log
   - Procurar por erros

3. **Teste imediatamente** após atualizar

4. **Cache do navegador**: Limpar com CTRL+SHIFT+R

### 📝 Exemplo Prático Completo:

```bash
# ==== NO SEU COMPUTADOR ====
cd /home/marco/ufal/minipar-interpreter-POO

# Fazer mudanças no código
nano src/lexer/Lexer.py

# Gerar novo arquivo
./prepare_pythonanywhere.sh

# ==== NO PYTHONANYWHERE ====
# 1. Upload minipar-pythonanywhere.tar.gz (via Files)

# 2. No Bash console:
cd ~
rm -rf minipar-interpreter
mkdir minipar-interpreter
tar -xzf minipar-pythonanywhere.tar.gz -C minipar-interpreter
cd minipar-interpreter
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 3. Web → Reload

# 4. Testar: http://seu_username.pythonanywhere.com
```

### 🔍 Verificar se Atualização Funcionou:

```bash
# No Bash console
cd ~/minipar-interpreter

# Ver data de modificação dos arquivos
ls -lh frontend/
ls -lh src/

# Ver versão no código (se você adicionar):
grep -r "VERSION" . | head -5
```

### 💡 Dica Pro:

Adicione versão no seu código para rastrear:

```python
# Em src/main.py ou similar
VERSION = "2025.11.01.1100"
print(f"MiniPar Interpreter v{VERSION}")
```

Ou no frontend:

```javascript
// Em frontend/home.js
console.log('MiniPar v2025.11.01.1100');
```

## ⚙️ Configurações Avançadas

### Aumentar Timeout

Arquivo WSGI, adicionar no início:
```python
import signal
signal.alarm(300)  # 5 minutos timeout
```

### Habilitar Debug

No WSGI, antes de `application`:
```python
DEBUG = True

def application(environ, start_response):
    if DEBUG:
        import traceback
        try:
            # ... código existente ...
        except Exception as e:
            error = traceback.format_exc()
            # Retornar erro detalhado
```

### Custom Domain

**Plano pago necessário**

1. Web → Add custom domain
2. Configure CNAME no seu DNS:
```
CNAME minipar -> seu_username.pythonanywhere.com
```

## 💰 Limitações Plano Gratuito

- ✅ 1 web app
- ✅ 512 MB espaço
- ✅ 100.000 requisições/dia
- ✅ CPU: 100 segundos/dia
- ⚠️ Site "dorme" após inatividade (acorda ao acessar)
- ❌ Sem WebSocket
- ❌ Sem HTTPS customizado
- ❌ Sem custom domains

### Upgrade para Paid ($5/mês)

Se precisar de mais:
- ✅ WebSocket support
- ✅ 10 web apps
- ✅ 1 GB espaço
- ✅ CPU ilimitado
- ✅ Always-on (não dorme)
- ✅ HTTPS customizado

## 📈 Monitoramento

### CPU Usage

Dashboard → mostra uso diário

### Disk Usage

Files → mostra espaço usado

### Database

MySQL gratuito (se precisar)

## 🔐 Segurança

### Variáveis de Ambiente

Bash console:
```bash
echo 'export SECRET_KEY="valor"' >> ~/.bashrc
source ~/.bashrc
```

No WSGI:
```python
import os
secret = os.environ.get('SECRET_KEY')
```

### Rate Limiting

Adicionar no WSGI:
```python
# TODO: Implementar rate limiting
# Rastrear IPs e limitar requisições
```

## 📚 Recursos

- 📖 [Documentação PythonAnywhere](https://help.pythonanywhere.com)
- 💬 [Fórum PythonAnywhere](https://www.pythonanywhere.com/forums/)
- 📧 [Suporte Email](mailto:support@pythonanywhere.com)

## ✅ Checklist

Antes de marcar como concluído:

- [ ] Conta PythonAnywhere criada
- [ ] Arquivo tar.gz preparado
- [ ] Upload feito
- [ ] Descompactado no servidor
- [x] Virtualenv criado e ativado
- [x] Dependências instaladas
- [x] Web app criada
- [x] Virtualenv path configurado
- [x] WSGI configurado (USERNAME correto!)
- [x] Static files configurados
- [x] Reload executado
- [ ] Site acessível
- [ ] Teste "Hello World" funciona
- [ ] API /interpretar funciona
- [ ] Logs sem erros

## 🎯 URL Final

Seu site estará em:
```
http://seu_username.pythonanywhere.com
```

## 💡 Dicas

1. **Username**: Escolha algo curto e profissional
2. **Backup**: Mantenha código no Git
3. **Logs**: Sempre verifique logs ao debugar
4. **Reload**: Sempre reload após mudanças
5. **CPU Limit**: Otimize código para não exceder limite diário

## 🆘 Suporte

Se precisar de ajuda:

1. Consulte Error log
2. Pesquise no fórum
3. Leia documentação oficial
4. Contate suporte (resposta em 24h)

---

**Pronto!** Seu MiniPar Interpreter está online gratuitamente! 🎉
