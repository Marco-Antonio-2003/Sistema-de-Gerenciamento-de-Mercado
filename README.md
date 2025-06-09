# 🏢 MB Sistema - Sistema de Gerenciamento Empresarial

Um sistema completo de gerenciamento empresarial desenvolvido em Python com PyQt5, incluindo PDV (Ponto de Venda), controle de estoque, gestão financeira e muito mais.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15+-green.svg)
![Status](https://img.shields.io/badge/status-Em%20Desenvolvimento-yellow.svg)


O **MB Sistema** é uma solução completa para gestão empresarial, desenvolvida para pequenas e médias empresas que precisam de um sistema integrado para controlar vendas, estoque, financeiro e relacionamento com clientes.

### ✨ Principais Diferenciais

- **Interface Moderna**: Design intuitivo e responsivo
- **PDV Avançado**: Sistema de vendas com leitor de código de barras
- **Sistema de Permissões**: Controle granular de acesso por funcionário
- **Sincronização**: Integração com Syncthing para backup automático
- **Assistente Virtual**: IA integrada para auxiliar nas operações
- **Multiplataforma**: Funciona em Windows, Linux e macOS

## 🚀 Funcionalidades

### 📊 Dashboard Principal
- Contadores em tempo real (Clientes, Produtos, Vendas)
- Informações do usuário logado
- Acesso rápido aos módulos principais
- Botão flutuante de contatos WhatsApp

### 🛒 PDV (Ponto de Venda)
- **Leitura de Código de Barras**: Suporte a leitores USB/Serial
- **Busca Inteligente**: Sistema de sugestões em tempo real
- **Múltiplas Formas de Pagamento**: Dinheiro, cartão, PIX, etc.
- **Cálculo de Troco**: Automático para pagamentos em dinheiro
- **Controle de Quantidade**: Suporte a `quantidade*código` (ex: `5*123`)
- **Impressão de Cupons**: Fiscal e não-fiscal
- **Gestão de Caixa**: Abertura/fechamento com controle

### 👥 Gestão de Pessoas
- Cadastro de clientes e fornecedores
- Histórico de transações
- Consulta de CPF/CNPJ online
- Sistema de relacionamento

### 📦 Controle de Estoque
- Cadastro completo de produtos
- Controle automático de estoque
- Alertas de estoque baixo
- Relatórios de movimentação

### 💰 Módulo Financeiro
- Controle de recebimentos
- Lançamentos financeiros
- Controle de caixa
- Classes financeiras
- Relatórios detalhados

## 🛠 Tecnologias Utilizadas

- **Python 3.7+**
- **PyQt5** - Interface gráfica
- **Firebird** - Banco de dados
- **Syncthing** - Sincronização de dados
- **SQLAlchemy** - ORM para banco de dados
- **Requests** - Requisições HTTP para APIs
- **ReportLab** - Geração de relatórios PDF

## 📋 Pré-requisitos

Antes de executar o projeto, certifique-se de ter instalado:

```bash
# Python 3.7 ou superior
python --version

# Pip (gerenciador de pacotes Python)
pip --version
```

## ⚙️ Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seuusuario/mb-sistema.git
cd mb-sistema
```

2. **Crie um ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate
```

3. **Instale as dependências**
```bash
pip install -r requirements.txt
```

4. **Configure o banco de dados**
```bash
# Execute o script de configuração inicial
python setup_database.py
```

5. **Execute o sistema**
```bash
python principal.py
```

## 🎮 Como Usar

### Primeiro Acesso

1. Execute o arquivo `principal.py`
2. Configure a conexão com o banco de dados
3. Crie o usuário administrador
4. Configure as permissões dos funcionários

### Acesso ao PDV

1. Clique em "Acesso ao PDV" na tela principal
2. Verifique se há um caixa aberto
3. Use o leitor de código de barras ou digite manualmente
4. Finalize a venda escolhendo a forma de pagamento

## 📚 Módulos do Sistema

### 🔧 GERAL
- **Cadastro de Empresa**: Informações da empresa
- **Cadastro de Clientes**: Gestão completa de clientes
- **Cadastro de Funcionários**: Controle de usuários e permissões
- **Consulta CNPJ**: Validação online de empresas

### 📦 PRODUTOS E SERVIÇOS
- **Produtos**: Cadastro completo com código de barras
- **Grupos**: Categorização de produtos
- **Unidades de Medida**: Controle de UMs

### 🛒 COMPRAS
- **Fornecedores**: Gestão de fornecedores
- **Pedidos**: Controle de compras

### 💸 VENDAS
- **Pedidos de Venda**: Gestão de vendas
- **PDV**: Ponto de venda integrado

### 💰 FINANCEIRO
- **Recebimentos**: Controle de recebimentos
- **Lançamentos**: Gestão financeira
- **Controle de Caixa**: PDV e movimentações
- **Conta Corrente**: Relacionamento financeiro
- **Classes Financeiras**: Categorização

### 📊 RELATÓRIOS
- **Vendas de Produtos**: Análise de vendas
- **Relatórios Fiscais**: NF-e, SAT, NFC-e

### ⚙️ FERRAMENTAS
- **Configuração de Estação**: Setup de impressoras
- **Configuração do Sistema**: Parâmetros gerais

## 🖥️ PDV - Ponto de Venda

### Funcionalidades Avançadas

#### 🔍 Sistema de Busca Inteligente
- **Sugestões em Tempo Real**: Digite e veja sugestões aparecerem
- **Busca por Múltiplos Campos**: Código, nome, código de barras
- **Navegação por Teclado**: Use setas ↑↓ e Enter

#### 📊 Controle de Quantidade
```bash
# Exemplos de uso:
5*123     # 5 unidades do produto 123
*10 456   # 10 unidades do produto 456
3* 789    # 3 unidades do produto 789
```

#### 💳 Formas de Pagamento
- **01** - Dinheiro (com cálculo de troco)
- **03** - Cartão de Crédito
- **04** - Cartão de Débito
- **17** - PIX
- E mais opções...

## ⌨️ Atalhos de Teclado

### Globais
- **F1** - Listar Clientes
- **F2** - Listar Produtos
- **F3** - Histórico de Vendas
- **F4** - Finalizar Venda
- **F5** - Editar Desconto
- **F6** - Editar Acréscimo
- **F7** - Fechar Caixa
- **F8** - Limpar Venda
- **F9** - Selecionar Forma de Pagamento
- **ESC** - Voltar/Cancelar

### PDV Específico
- **Enter** - Confirmar/Buscar produto
- **↑↓** - Navegar sugestões
- **+/-** - Ajustar quantidade
- **Tab** - Navegar entre campos

### 📝 Padrões de Código

- Use **docstrings** para documentar funções
- Siga o padrão **PEP 8**
- Comente código complexo
- Teste suas mudanças antes do commit

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
