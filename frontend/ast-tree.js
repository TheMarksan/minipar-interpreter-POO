/**
 * ast-tree.js
 * Biblioteca para renderizar AST (Abstract Syntax Tree) como árvore visual hierárquica
 */

class ASTTreeRenderer {
  constructor(containerElement) {
    this.container = containerElement;
    this.nodeCount = 0;
  }

  /**
   * Renderiza a AST como uma árvore visual HTML
   * @param {Object|string} astData - Dados da AST (objeto ou string)
   */
  render(astData) {
    this.container.innerHTML = '';
    this.nodeCount = 0;

    // Se recebeu string, tentar parsear como JSON
    let ast = astData;
    if (typeof astData === 'string') {
      try {
        ast = JSON.parse(astData);
      } catch (e) {
        // Se não for JSON, renderizar como texto
        this.renderTextAST(astData);
        return;
      }
    }

    // Criar elemento raiz
    const tree = document.createElement('div');
    tree.className = 'ast-tree';
    
    // Renderizar nó raiz
    const rootNode = this.createNode(ast, 'Program');
    tree.appendChild(rootNode);

    this.container.appendChild(tree);
    
    // Adicionar estatísticas
    const stats = document.createElement('div');
    stats.className = 'ast-stats';
    stats.innerHTML = `<span class="meta">Total de nós: ${this.nodeCount}</span>`;
    this.container.appendChild(stats);
  }

  /**
   * Renderiza AST textual (formato string do backend)
   */
  renderTextAST(textData) {
    const pre = document.createElement('pre');
    pre.className = 'ast-text';
    pre.style.fontFamily = 'monospace';
    pre.style.fontSize = '13px';
    pre.style.lineHeight = '1.6';
    pre.style.whiteSpace = 'pre-wrap';
    pre.style.color = 'var(--text)';
    
    // Processar o texto para adicionar cores e indentação
    const lines = textData.split('\n');
    let html = '';
    
    lines.forEach(line => {
      if (line.includes('Program:')) {
        html += `<span style="color: #50fa7b; font-weight: bold;">${this.escapeHtml(line)}</span>\n`;
      } else if (line.includes('SEQ {') || line.includes('PAR {')) {
        html += `<span style="color: #8be9fd; font-weight: bold;">${this.escapeHtml(line)}</span>\n`;
      } else if (line.includes('var ') || line.includes('CLASS ') || line.includes('FLOAT ') || line.includes('INT ')) {
        html += `<span style="color: #ff79c6;">${this.escapeHtml(line)}</span>\n`;
      } else if (line.includes('for ') || line.includes('if ') || line.includes('while ')) {
        html += `<span style="color: #ffb86c;">${this.escapeHtml(line)}</span>\n`;
      } else if (line.includes('print(') || line.includes('return ')) {
        html += `<span style="color: #f1fa8c;">${this.escapeHtml(line)}</span>\n`;
      } else {
        html += `${this.escapeHtml(line)}\n`;
      }
    });
    
    pre.innerHTML = html;
    this.container.appendChild(pre);
  }

  /**
   * Cria um nó da árvore
   */
  createNode(data, label = '') {
    this.nodeCount++;
    
    const nodeWrapper = document.createElement('div');
    nodeWrapper.className = 'ast-node-wrapper';

    const node = document.createElement('div');
    node.className = 'ast-node';
    
    // Determinar tipo e cor do nó
    const nodeType = this.getNodeType(data, label);
    node.classList.add(`node-${nodeType}`);
    
    // Criar conteúdo do nó
    const nodeContent = document.createElement('div');
    nodeContent.className = 'ast-node-content';
    
    const nodeLabel = document.createElement('span');
    nodeLabel.className = 'ast-node-label';
    nodeLabel.textContent = this.formatNodeLabel(data, label);
    nodeContent.appendChild(nodeLabel);
    
    // Adicionar detalhes do nó
    const details = this.getNodeDetails(data);
    if (details) {
      const nodeDetails = document.createElement('span');
      nodeDetails.className = 'ast-node-details';
      nodeDetails.textContent = details;
      nodeContent.appendChild(nodeDetails);
    }
    
    node.appendChild(nodeContent);
    nodeWrapper.appendChild(node);

    // Processar filhos
    const children = this.getChildren(data);
    if (children && children.length > 0) {
      const childrenContainer = document.createElement('div');
      childrenContainer.className = 'ast-children';
      
      children.forEach(child => {
        const childNode = this.createNode(child.data, child.label);
        childrenContainer.appendChild(childNode);
      });
      
      nodeWrapper.appendChild(childrenContainer);
    }

    return nodeWrapper;
  }

  /**
   * Determina o tipo do nó para estilização
   */
  getNodeType(data, label) {
    if (!data) return 'default';
    
    const typeMap = {
      'Program': 'root',
      'SEQ': 'block',
      'PAR': 'block',
      'CLASS': 'class',
      'Function': 'function',
      'Method': 'function',
      'Declaration': 'declaration',
      'Assignment': 'assignment',
      'IfNode': 'control',
      'ForNode': 'control',
      'WhileNode': 'control',
      'print': 'io',
      'return': 'control'
    };
    
    const labelLower = label.toLowerCase();
    for (const [key, value] of Object.entries(typeMap)) {
      if (labelLower.includes(key.toLowerCase())) {
        return value;
      }
    }
    
    if (data.type) {
      const typeLower = data.type.toLowerCase();
      for (const [key, value] of Object.entries(typeMap)) {
        if (typeLower.includes(key.toLowerCase())) {
          return value;
        }
      }
    }
    
    return 'default';
  }

  /**
   * Formata o label do nó
   */
  formatNodeLabel(data, label) {
    if (label) return label;
    if (data && data.type) return data.type;
    if (typeof data === 'object' && data !== null) {
      const keys = Object.keys(data);
      if (keys.length > 0) return keys[0];
    }
    return 'Node';
  }

  /**
   * Extrai detalhes do nó
   */
  getNodeDetails(data) {
    if (!data || typeof data !== 'object') return '';
    
    const details = [];
    
    if (data.name) details.push(`name: ${data.name}`);
    if (data.identifier) details.push(`id: ${data.identifier}`);
    if (data.type_name) details.push(`type: ${data.type_name}`);
    if (data.operator) details.push(`op: ${data.operator}`);
    if (data.value !== undefined && data.value !== null) {
      const val = typeof data.value === 'string' ? `"${data.value}"` : data.value;
      details.push(`val: ${val}`);
    }
    
    return details.length > 0 ? `(${details.join(', ')})` : '';
  }

  /**
   * Extrai filhos do nó
   */
  getChildren(data) {
    if (!data || typeof data !== 'object') return [];
    
    const children = [];
    
    // Priorizar campos conhecidos
    if (data.children && Array.isArray(data.children)) {
      data.children.forEach((child, idx) => {
        children.push({ data: child, label: `child_${idx}` });
      });
    }
    
    if (data.statements && Array.isArray(data.statements)) {
      data.statements.forEach((stmt, idx) => {
        children.push({ data: stmt, label: this.formatNodeLabel(stmt, `stmt_${idx}`) });
      });
    }
    
    if (data.body && Array.isArray(data.body)) {
      data.body.forEach((stmt, idx) => {
        children.push({ data: stmt, label: this.formatNodeLabel(stmt, `body_${idx}`) });
      });
    }
    
    if (data.then_body && Array.isArray(data.then_body)) {
      const thenBranch = document.createElement('div');
      data.then_body.forEach((stmt, idx) => {
        children.push({ data: stmt, label: `then_${idx}` });
      });
    }
    
    if (data.else_body && Array.isArray(data.else_body)) {
      data.else_body.forEach((stmt, idx) => {
        children.push({ data: stmt, label: `else_${idx}` });
      });
    }
    
    // Campos individuais importantes
    if (data.condition) {
      children.push({ data: data.condition, label: 'condition' });
    }
    
    if (data.expression) {
      children.push({ data: data.expression, label: 'expression' });
    }
    
    if (data.left) {
      children.push({ data: data.left, label: 'left' });
    }
    
    if (data.right) {
      children.push({ data: data.right, label: 'right' });
    }
    
    return children;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
}

// Exportar para uso global
window.ASTTreeRenderer = ASTTreeRenderer;
