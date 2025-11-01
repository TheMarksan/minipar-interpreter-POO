# 🚀 Guia de Deploy no PythonAnywhere

Este guia mostra como fazer deploy do MiniPar Interpreter no PythonAnywhere.

## 📋 Pré-requisitos

1. Conta no [PythonAnywhere](https://www.pythonanywhere.com/)
2. Plano gratuito ou pago (gratuito funciona perfeitamente)
3. Código do projeto no PythonAnywhere

---

## 🔧 Passo 1: Fazer Upload do Projeto

### Opção A: Via Git (Recomendado)

```bash
# No terminal do PythonAnywhere (bash console)
cd ~
git clone https://github.com/TheMarksan/minipar-interpreter-POO.git
cd minipar-interpreter-POO
```

### Opção B: Via Upload de Arquivos

1. Vá em **Files** no dashboard do PythonAnywhere
2. Crie pasta `minipar-interpreter-POO`
3. Faça upload de todos os arquivos do projeto

---

## 🌐 Passo 2: Criar Web App

1. Vá em **Web** no dashboard
2. Clique em **Add a new web app**
3. Escolha **Manual configuration** (não use Flask quickstart)
4. Escolha **Python 3.10** (ou mais recente)
5. Clique em **Next**

---

## ⚙️ Passo 3: Configurar WSGI File

1. Na página da Web App, clique em **WSGI configuration file**
2. **Apague todo o conteúdo** do arquivo
3. Cole o seguinte código:

```python
import sys
import os

# Adicionar o caminho do projeto ao sys.path
path = '/home/SEU_USUARIO/minipar-interpreter-POO'
if path not in sys.path:
    sys.path.insert(0, path)

# Importar a aplicação Flask
from server_pythonanywhere import app as application
```

**⚠️ IMPORTANTE:** Substitua `SEU_USUARIO` pelo seu username do PythonAnywhere!

4. Clique em **Save**

---

## 📦 Passo 4: Instalar Dependências

1. Abra um **Bash console** no PythonAnywhere
2. Execute:

```bash
cd ~/minipar-interpreter-POO
pip3 install --user flask flask-cors
```

---

## 📁 Passo 5: Configurar Static Files (Opcional mas Recomendado)

Na página da Web App, na seção **Static files**:

1. Clique em **Enter URL** e digite: `/static`
2. Clique em **Enter path** e digite: `/home/SEU_USUARIO/minipar-interpreter-POO/frontend`

Isso fará o servidor servir arquivos CSS/JS diretamente sem passar pelo Flask.

---

## 🔄 Passo 6: Recarregar a Aplicação

1. Na página da Web App, clique no botão verde **Reload SEU_USUARIO.pythonanywhere.com**
2. Aguarde alguns segundos

---

## ✅ Passo 7: Testar

1. Acesse: `https://SEU_USUARIO.pythonanywhere.com`
2. Você deve ver a interface do MiniPar Interpreter
3. Teste executando algum código

---

## 🔍 Troubleshooting (Resolução de Problemas)

### Erro 502 Bad Gateway

**Causa:** Problema no WSGI ou importação do Flask.

**Solução:**
1. Verifique o **Error log** na página Web App
2. Certifique-se que Flask está instalado: `pip3 install --user flask flask-cors`
3. Verifique se o caminho no WSGI está correto

### Erro 404 Not Found

**Causa:** Arquivos do frontend não estão sendo encontrados.

**Solução:**
1. Verifique se a pasta `frontend` existe em `/home/SEU_USUARIO/minipar-interpreter-POO/`
2. Configure Static Files (Passo 5)

### Erro "ModuleNotFoundError"

**Causa:** Dependências não instaladas ou caminho incorreto.

**Solução:**
```bash
cd ~/minipar-interpreter-POO
pip3 install --user flask flask-cors
```

### Verificar logs de erro

1. Na página Web App, clique em **Error log**
2. Ou acesse: `/var/log/SEU_USUARIO.pythonanywhere.com.error.log`

---

## 🧪 Testando Localmente no PythonAnywhere

Antes de configurar como Web App, teste localmente:

```bash
cd ~/minipar-interpreter-POO
python3 server_pythonanywhere.py --port 8000
```

Depois abra um navegador e acesse o URL que aparece.

---

## 🌍 Acessando de Outras Redes

### Seu site estará disponível em:

```
https://SEU_USUARIO.pythonanywhere.com
```

✅ Pode ser acessado de **qualquer lugar do mundo**  
✅ Funciona em **qualquer rede** (WiFi, dados móveis, etc.)  
✅ Não precisa configurar firewall ou roteador  
✅ HTTPS gratuito incluído  

### Compartilhando o link:

Simplesmente envie o link para outras pessoas:
```
https://SEU_USUARIO.pythonanywhere.com
```

---

## 🔄 Atualizando o Código

Quando fizer mudanças no código:

```bash
# Se usou Git
cd ~/minipar-interpreter-POO
git pull

# Depois, sempre recarregue a aplicação
# Vá em Web > Reload SEU_USUARIO.pythonanywhere.com
```

---

## 📊 Limitações do Plano Gratuito

- **Tráfego:** Limitado (suficiente para uso educacional)
- **Uptime:** Site pode "dormir" após 3 meses de inatividade
- **CPU:** Limitado (suficiente para interpretador)
- **Sem WebSocket:** Apenas HTTP/HTTPS (por isso removemos WebSocket)

---

## 🔐 Considerações de Segurança

### Para uso em produção/avaliação:

1. **Limite de execução:** Adicionar timeout para evitar loops infinitos
2. **Rate limiting:** Limitar número de requisições por IP
3. **Sanitização:** Código já está relativamente seguro (interpretador isolado)

---

## 📞 Suporte

- **Documentação PythonAnywhere:** https://help.pythonanywhere.com/
- **Fórum PythonAnywhere:** https://www.pythonanywhere.com/forums/

---

## ✨ Recursos Extras

### Domínio Customizado (Plano Pago)

No plano pago, você pode usar seu próprio domínio:
```
https://minipar.seusite.com
```

### HTTPS Automático

PythonAnywhere fornece HTTPS automaticamente, sem necessidade de configuração.

---

## 🎯 Checklist Final

- [ ] Projeto no PythonAnywhere
- [ ] Flask e Flask-CORS instalados
- [ ] Web App criada (Manual Configuration)
- [ ] WSGI configurado com caminho correto
- [ ] Static files configurados (opcional)
- [ ] Aplicação recarregada
- [ ] Site testado: `https://SEU_USUARIO.pythonanywhere.com`
- [ ] Código funciona em outras redes ✅

---

**Pronto! Seu interpretador MiniPar agora está online e acessível de qualquer lugar! 🚀**
