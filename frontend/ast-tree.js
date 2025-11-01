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
    
    const type = data.type || label || '';
    const typeLower = type.toLowerCase();
    
    // Categorias de nós
    if (typeLower.includes('program')) return 'root';
    if (typeLower.includes('class')) return 'class';
    if (typeLower.includes('function') || typeLower.includes('method')) return 'function';
    if (typeLower.includes('block') || typeLower === 'seq' || typeLower === 'par') return 'block';
    
    // Controle de fluxo
    if (typeLower.includes('if') || typeLower.includes('while') || 
        typeLower.includes('for') || typeLower.includes('return')) return 'control';
    
    // Declarações e atribuições
    if (typeLower.includes('declaration') || typeLower.includes('attribute')) return 'declaration';
    if (typeLower.includes('assignment')) return 'assignment';
    
    // I/O
    if (typeLower.includes('print') || typeLower.includes('input') || 
        typeLower.includes('send') || typeLower.includes('receive')) return 'io';
    
    // Operações
    if (typeLower.includes('binaryop') || typeLower.includes('unaryop') || 
        typeLower.includes('condition')) return 'operation';
    
    // Valores e identificadores
    if (typeLower.includes('number') || typeLower.includes('string') || 
        typeLower.includes('identifier')) return 'literal';
    
    // Arrays e acesso
    if (typeLower.includes('array')) return 'array';
    
    // Chamadas
    if (typeLower.includes('call')) return 'call';
    
    // Objetos
    if (typeLower.includes('new') || typeLower.includes('instantiation')) return 'object';
    
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
    
    // Informações de identificação
    if (data.name) details.push(`name: ${data.name}`);
    if (data.identifier) details.push(`id: ${data.identifier}`);
    if (data.var_name) details.push(`var: ${data.var_name}`);
    if (data.class_name) details.push(`class: ${data.class_name}`);
    if (data.method_name) details.push(`method: ${data.method_name}`);
    if (data.object_name) details.push(`obj: ${data.object_name}`);
    if (data.attribute_name) details.push(`attr: ${data.attribute_name}`);
    if (data.array_name) details.push(`array: ${data.array_name}`);
    
    // Tipos
    if (data.type_name) details.push(`type: ${data.type_name}`);
    if (data.return_type) details.push(`returns: ${data.return_type}`);
    if (data.block_type) details.push(`block: ${data.block_type}`);
    
    // Operadores e valores
    if (data.operator) details.push(`op: ${data.operator}`);
    if (data.value !== undefined && data.value !== null) {
      const val = typeof data.value === 'string' ? `"${data.value}"` : data.value;
      details.push(`val: ${val}`);
    }
    
    // Arrays
    if (data.is_array) details.push('is_array');
    if (data.is_2d_array) details.push('is_2d_array');
    
    // Outros
    if (data.parent) details.push(`extends: ${data.parent}`);
    if (data.text) details.push(`text: "${data.text.substring(0, 30)}..."`);
    if (data.prompt) details.push(`prompt: "${data.prompt}"`);
    if (data.channel) details.push(`channel: ${data.channel}`);
    
    return details.length > 0 ? `(${details.join(', ')})` : '';
  }

  /**
   * Extrai filhos do nó
   */
  getChildren(data) {
    if (!data || typeof data !== 'object') return [];
    
    const children = [];
    
    // Arrays de nós
    const arrayFields = [
      'children', 'statements', 'body', 'then_body', 'else_body',
      'attributes', 'methods', 'parameters', 'arguments', 'values',
      'elements', 'variables'
    ];
    
    arrayFields.forEach(field => {
      if (data[field] && Array.isArray(data[field]) && data[field].length > 0) {
        data[field].forEach((item, idx) => {
          if (item && typeof item === 'object') {
            const label = this.formatNodeLabel(item, `${field}_${idx}`);
            children.push({ data: item, label: label });
          }
        });
      }
    });
    
    // Nós individuais importantes
    const singleNodeFields = [
      'condition', 'expression', 'left', 'right', 'operand',
      'init_expr', 'increment', 'initial_value', 'index', 'index2',
      'array_access', 'object_attr_access', 'array_size', 'object',
      'then_block', 'else_block'
    ];
    
    singleNodeFields.forEach(field => {
      if (data[field] && typeof data[field] === 'object') {
        children.push({ 
          data: data[field], 
          label: field 
        });
      }
    });
    
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
