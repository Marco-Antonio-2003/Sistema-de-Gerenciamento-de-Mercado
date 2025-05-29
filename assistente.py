# assistente.py - Versão integrada com banco de dados
import json
import requests
from datetime import datetime
import os
import sys
import re
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                            QLineEdit, QPushButton, QLabel, QApplication,
                            QDockWidget, QMainWindow, QMessageBox, QFrame, 
                            QScrollArea, QSizePolicy, QGraphicsOpacityEffect
                           )
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QThread, pyqtSlot, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QTextCursor, QFont, QColor, QPalette, QTextDocument, QTextOption, QIcon

# Importar funções do banco de dados
try:
    from base.banco import (
        execute_query, listar_pessoas, listar_funcionarios, listar_produtos,
        listar_fornecedores, listar_empresas, listar_recebimentos_pendentes,
        listar_caixas, listar_pedidos_venda, listar_contas_correntes,
        obter_vendas_por_periodo, verificar_produtos_estoque_baixo
    )
except ImportError:
    print("Erro ao importar funções do banco de dados")
    execute_query = None


class BancoDadosAssistente:
    """Classe para consultar dados do banco e responder perguntas"""
    
    def __init__(self):
        self.padroes_perguntas = {
            # Clientes/Pessoas
            r'quantos?\s*clientes?': self.contar_clientes,
            r'número\s*de\s*clientes?': self.contar_clientes,
            r'total\s*de\s*clientes?': self.contar_clientes,
            
            # Funcionários
            r'quantos?\s*funcionários?': self.contar_funcionarios,
            r'número\s*de\s*funcionários?': self.contar_funcionarios,
            r'total\s*de\s*funcionários?': self.contar_funcionarios,
            
            # Produtos
            r'quantos?\s*produtos?': self.contar_produtos,
            r'número\s*de\s*produtos?': self.contar_produtos,
            r'total\s*de\s*produtos?': self.contar_produtos,
            r'estoque\s*baixo': self.produtos_estoque_baixo,
            
            # Fornecedores 
            r'quantos?\s*fornecedores?': self.contar_fornecedores,
            r'número\s*de\s*fornecedores?': self.contar_fornecedores,
            
            # Empresas
            r'quantas?\s*empresas?': self.contar_empresas,
            r'número\s*de\s*empresas?': self.contar_empresas,
            
            # Recebimentos
            r'recebimentos?\s*pendentes?': self.contar_recebimentos_pendentes,
            r'contas?\s*a\s*receber': self.contar_recebimentos_pendentes,
            r'valores?\s*a\s*receber': self.valor_total_receber,
            
            # Caixas
            r'caixas?\s*abertos?': self.caixas_abertos,
            r'situação\s*do\s*caixa': self.situacao_caixa,
            
            # Pedidos
            r'pedidos?\s*de\s*venda': self.contar_pedidos_venda,
            r'vendas?\s*do\s*mês': self.vendas_mes_atual,
            
            # Contas correntes
            r'contas?\s*correntes?': self.contar_contas_correntes,
            
            # Resumo geral
            r'resumo\s*geral': self.resumo_geral,
            r'dashboard': self.resumo_geral,
            r'visão\s*geral': self.resumo_geral,
        }
    
    def processar_pergunta(self, pergunta):
        """
        Verifica se a pergunta é sobre dados do sistema e retorna resposta
        
        Args:
            pergunta (str): Pergunta do usuário
            
        Returns:
            tuple: (bool, str) - (é_pergunta_dados, resposta)
        """
        if not execute_query:
            return False, ""
            
        pergunta_lower = pergunta.lower().strip()
        
        # Verificar cada padrão
        for padrao, funcao in self.padroes_perguntas.items():
            if re.search(padrao, pergunta_lower):
                try:
                    resposta = funcao()
                    return True, resposta
                except Exception as e:
                    print(f"Erro ao executar consulta: {e}")
                    return True, f"❌ Erro ao consultar dados: {str(e)}"
        
        return False, ""
    
    def contar_clientes(self):
        """Conta o número total de clientes"""
        try:
            pessoas = listar_pessoas()
            total = len(pessoas) if pessoas else 0
            
            if total == 0:
                return "📊 Você não possui clientes cadastrados ainda."
            elif total == 1:
                return "📊 Você tem **1 cliente** cadastrado no sistema."
            else:
                return f"📊 Você tem **{total} clientes** cadastrados no sistema."
        except:
            # Fallback usando query direta
            result = execute_query("SELECT COUNT(*) FROM PESSOAS")
            total = result[0][0] if result else 0
            return f"📊 Você tem **{total} clientes** cadastrados no sistema."
    
    def contar_funcionarios(self):
        """Conta o número total de funcionários"""
        try:
            funcionarios = listar_funcionarios()
            total = len(funcionarios) if funcionarios else 0
            
            if total == 0:
                return "👥 Nenhum funcionário cadastrado no sistema."
            elif total == 1:
                return "👥 Você tem **1 funcionário** cadastrado."
            else:
                return f"👥 Você tem **{total} funcionários** cadastrados."
        except:
            result = execute_query("SELECT COUNT(*) FROM FUNCIONARIOS")
            total = result[0][0] if result else 0
            return f"👥 Você tem **{total} funcionários** cadastrados."
    
    def contar_produtos(self):
        """Conta o número total de produtos"""
        try:
            produtos = listar_produtos()
            total = len(produtos) if produtos else 0
            
            if total == 0:
                return "📦 Nenhum produto cadastrado no sistema."
            elif total == 1:
                return "📦 Você tem **1 produto** cadastrado."
            else:
                return f"📦 Você tem **{total} produtos** cadastrados no sistema."
        except:
            result = execute_query("SELECT COUNT(*) FROM PRODUTOS")
            total = result[0][0] if result else 0
            return f"📦 Você tem **{total} produtos** cadastrados."
    
    def produtos_estoque_baixo(self):
        """Verifica produtos com estoque baixo"""
        try:
            produtos_baixo = verificar_produtos_estoque_baixo(limite=5)
            
            if not produtos_baixo:
                return "✅ Todos os produtos estão com estoque adequado!"
            
            total = len(produtos_baixo)
            resposta = f"⚠️ **{total} produtos** com estoque baixo:\n\n"
            
            for produto in produtos_baixo[:5]:  # Mostrar apenas os primeiros 5
                resposta += f"• **{produto['nome']}** - Estoque: {produto['estoque']}\n"
            
            if total > 5:
                resposta += f"\n... e mais {total - 5} produtos."
                
            return resposta
        except:
            return "❌ Erro ao verificar estoque dos produtos."
    
    def contar_fornecedores(self):
        """Conta o número total de fornecedores"""
        try:
            fornecedores = listar_fornecedores()
            total = len(fornecedores) if fornecedores else 0
            
            if total == 0:
                return "🏭 Nenhum fornecedor cadastrado."
            elif total == 1:
                return "🏭 Você tem **1 fornecedor** cadastrado."
            else:
                return f"🏭 Você tem **{total} fornecedores** cadastrados."
        except:
            result = execute_query("SELECT COUNT(*) FROM FORNECEDORES")
            total = result[0][0] if result else 0
            return f"🏭 Você tem **{total} fornecedores** cadastrados."
    
    def contar_empresas(self):
        """Conta o número total de empresas"""
        try:
            empresas = listar_empresas()
            total = len(empresas) if empresas else 0
            
            if total == 0:
                return "🏢 Nenhuma empresa cadastrada."
            elif total == 1:
                return "🏢 Você tem **1 empresa** cadastrada."
            else:
                return f"🏢 Você tem **{total} empresas** cadastradas."
        except:
            result = execute_query("SELECT COUNT(*) FROM EMPRESAS")
            total = result[0][0] if result else 0
            return f"🏢 Você tem **{total} empresas** cadastradas."
    
    def contar_recebimentos_pendentes(self):
        """Conta recebimentos pendentes"""
        try:
            recebimentos = listar_recebimentos_pendentes()
            total = len(recebimentos) if recebimentos else 0
            
            if total == 0:
                return "✅ Não há recebimentos pendentes!"
            elif total == 1:
                return "💰 Você tem **1 recebimento** pendente."
            else:
                return f"💰 Você tem **{total} recebimentos** pendentes."
        except:
            result = execute_query("SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES WHERE STATUS = 'Pendente'")
            total = result[0][0] if result else 0
            return f"💰 Você tem **{total} recebimentos** pendentes."
    
    def valor_total_receber(self):
        """Calcula valor total a receber"""
        try:
            result = execute_query("SELECT SUM(VALOR) FROM RECEBIMENTOS_CLIENTES WHERE STATUS = 'Pendente'")
            total = result[0][0] if result and result[0][0] else 0
            
            if total == 0:
                return "✅ Não há valores pendentes de recebimento!"
            else:
                return f"💰 Valor total a receber: **R$ {total:,.2f}**".replace(',', 'X').replace('.', ',').replace('X', '.')
        except:
            return "❌ Erro ao calcular valores a receber."
    
    def caixas_abertos(self):
        """Verifica caixas abertos"""
        try:
            result = execute_query("SELECT COUNT(*) FROM CAIXA_CONTROLE WHERE STATUS = 'A'")
            total = result[0][0] if result else 0
            
            if total == 0:
                return "🔒 Nenhum caixa está aberto no momento."
            elif total == 1:
                return "🔓 Há **1 caixa aberto** no momento."
            else:
                return f"🔓 Há **{total} caixas abertos** no momento."
        except:
            return "❌ Erro ao verificar situação dos caixas."
    
    def situacao_caixa(self):
        """Mostra situação geral dos caixas"""
        try:
            abertos = execute_query("SELECT COUNT(*) FROM CAIXA_CONTROLE WHERE STATUS = 'A'")[0][0]
            fechados_hoje = execute_query("SELECT COUNT(*) FROM CAIXA_CONTROLE WHERE STATUS = 'F' AND DATA_FECHAMENTO = CURRENT_DATE")[0][0]
            
            resposta = f"💳 **Situação dos Caixas:**\n"
            resposta += f"• Caixas abertos: **{abertos}**\n"
            resposta += f"• Caixas fechados hoje: **{fechados_hoje}**"
            
            return resposta
        except:
            return "❌ Erro ao verificar situação dos caixas."
    
    def contar_pedidos_venda(self):
        """Conta pedidos de venda"""
        try:
            pedidos = listar_pedidos_venda()
            total = len(pedidos) if pedidos else 0
            
            if total == 0:
                return "📋 Nenhum pedido de venda cadastrado."
            elif total == 1:
                return "📋 Você tem **1 pedido** de venda."
            else:
                return f"📋 Você tem **{total} pedidos** de venda."
        except:
            result = execute_query("SELECT COUNT(*) FROM PEDIDOS_VENDA")
            total = result[0][0] if result else 0
            return f"📋 Você tem **{total} pedidos** de venda."
    
    def vendas_mes_atual(self):
        """Mostra vendas do mês atual"""
        try:
            from datetime import date
            hoje = date.today()
            primeiro_dia = date(hoje.year, hoje.month, 1)
            
            # Verificar se a tabela VENDAS_PRODUTOS existe
            result = execute_query(f"""
                SELECT SUM(VALOR_TOTAL), COUNT(*) 
                FROM VENDAS_PRODUTOS 
                WHERE DATA BETWEEN '{primeiro_dia}' AND '{hoje}'
            """)
            
            if result and result[0][0]:
                valor_total = result[0][0]
                quantidade = result[0][1]
                return f"📊 **Vendas deste mês:**\n• Quantidade: **{quantidade}** vendas\n• Valor total: **R$ {valor_total:,.2f}**".replace(',', 'X').replace('.', ',').replace('X', '.')
            else:
                return "📊 Nenhuma venda registrada este mês."
        except:
            return "❌ Erro ao consultar vendas do mês."
    
    def contar_contas_correntes(self):
        """Conta contas correntes"""
        try:
            contas = listar_contas_correntes()
            total = len(contas) if contas else 0
            
            if total == 0:
                return "💳 Nenhuma conta corrente cadastrada."
            elif total == 1:
                return "💳 Você tem **1 conta corrente** cadastrada."
            else:
                return f"💳 Você tem **{total} contas correntes** cadastradas."
        except:
            result = execute_query("SELECT COUNT(*) FROM CONTAS_CORRENTES")
            total = result[0][0] if result else 0
            return f"💳 Você tem **{total} contas correntes** cadastradas."
    
    def resumo_geral(self):
        """Fornece um resumo geral do sistema"""
        try:
            resumo = "📊 **RESUMO GERAL DO SISTEMA**\n\n"
            
            # Clientes
            clientes = execute_query("SELECT COUNT(*) FROM PESSOAS")[0][0]
            resumo += f"👥 **Clientes:** {clientes}\n"
            
            # Produtos
            produtos = execute_query("SELECT COUNT(*) FROM PRODUTOS")[0][0]
            resumo += f"📦 **Produtos:** {produtos}\n"
            
            # Funcionários
            funcionarios = execute_query("SELECT COUNT(*) FROM FUNCIONARIOS")[0][0]
            resumo += f"👨‍💼 **Funcionários:** {funcionarios}\n"
            
            # Fornecedores
            fornecedores = execute_query("SELECT COUNT(*) FROM FORNECEDORES")[0][0]
            resumo += f"🏭 **Fornecedores:** {fornecedores}\n"
            
            # Recebimentos pendentes
            recebimentos_pendentes = execute_query("SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES WHERE STATUS = 'Pendente'")[0][0]
            resumo += f"💰 **Recebimentos pendentes:** {recebimentos_pendentes}\n"
            
            # Valor a receber
            valor_receber = execute_query("SELECT COALESCE(SUM(VALOR), 0) FROM RECEBIMENTOS_CLIENTES WHERE STATUS = 'Pendente'")[0][0]
            resumo += f"💵 **Valor a receber:** R$ {valor_receber:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
            
            return resumo
        except Exception as e:
            return f"❌ Erro ao gerar resumo: {str(e)}"


class AssistenteAPI(QThread):
    """Thread otimizada para fazer requisições com streaming"""
    texto_parcial = pyqtSignal(str)  # Para streaming
    resposta_completa = pyqtSignal(str)
    erro_ocorrido = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.api_key = "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"
        self.mensagem = ""
        self.historico_conversa = []
        self.use_streaming = True  # Ativar streaming
        self.banco_assistente = BancoDadosAssistente()  # Instância para consultas do banco
        
    def configurar_mensagem(self, mensagem, historico=[], use_streaming=True):
        """Configura a mensagem e opções para a próxima requisição"""
        self.mensagem = mensagem
        self.historico_conversa = historico
        self.use_streaming = use_streaming
        
    def run(self):
        """Executa a requisição otimizada à API"""
        try:
            # Primeiro, verificar se é uma pergunta sobre dados do sistema
            eh_pergunta_dados, resposta_dados = self.banco_assistente.processar_pergunta(self.mensagem)
            
            if eh_pergunta_dados:
                # Se é uma pergunta sobre dados, responder diretamente
                self.resposta_completa.emit(resposta_dados)
                return
            
            # Se não é pergunta sobre dados, continuar com a API externa
            messages = [
                {
                    "role": "system",
                    "content": """Você é o assistente virtual especializado do MB Sistema - Sistema de Gerenciamento Empresarial.

**INSTRUÇÕES DE RESPOSTA:**
- Seja DIRETO e CONCISO
- Use linguagem clara e profissional
- Responda em português brasileiro
- Use emojis moderadamente (máximo 2 por resposta)
- Forneça passos específicos quando solicitado

**CAPACIDADES ESPECIAIS:**
🔍 **CONSULTAS DE DADOS** - Posso fornecer informações sobre:
• Quantos clientes, produtos, funcionários você tem
• Recebimentos pendentes e valores a receber
• Situação dos caixas e pedidos de venda
• Produtos com estoque baixo
• Resumo geral do sistema

**MÓDULOS DO SISTEMA:**

🏢 **GERAL:**
• Cadastro de empresa - Dados da empresa
• Cadastro de Clientes - Gerenciar clientes/pessoas
• Cadastro Funcionários - Gestão de funcionários
• Consulta CNPJ - Validação de dados empresariais

📦 **PRODUTOS E SERVIÇOS:**
• Produtos - Cadastro e gestão de produtos
• Grupo de produtos - Categorização
• Unidade de medida - Configurações de medidas

🛒 **COMPRAS:**
• Fornecedores - Cadastro e gestão de fornecedores

💰 **VENDAS:**
• Pedido de vendas - Criação de vendas
• Clientes - Gestão comercial

💳 **FINANCEIRO:**
• Recebimento de clientes - Contas a receber
• Lançamento Financeiro - Movimentações
• Controle de caixa (PDV) - Ponto de venda
• Conta corrente - Movimentações bancárias
• Classes financeiras - Categorização

📊 **RELATÓRIOS:**
• Relatório de Vendas - Análise de vendas
• Fiscal NF-e, SAT, NFC-e - Documentos fiscais

⚙️ **FERRAMENTAS:**
• Configuração de estação - Impressoras
• Configuração do Sistema - Ajustes gerais

🏪 **PDV:** Botão verde no canto superior esquerdo

**INSTRUÇÕES DE NAVEGAÇÃO:**
- Para acessar qualquer módulo: "Menu [CATEGORIA] → [MÓDULO]"
- PDV: Clique no botão verde "Acesso ao PDV"
- Seja específico sobre onde encontrar cada funcionalidade

**EXEMPLOS DE PERGUNTAS SOBRE DADOS:**
- "Quantos clientes eu tenho?"
- "Qual o valor total a receber?"
- "Produtos com estoque baixo"
- "Resumo geral do sistema"
- "Situação do caixa"""
                }
            ]
            
            # Limitar histórico para melhor performance (últimas 6 mensagens)
            historico_limitado = self.historico_conversa[-6:] if len(self.historico_conversa) > 6 else self.historico_conversa
            messages.extend(historico_limitado)
            messages.append({"role": "user", "content": self.mensagem})
            
            # Parâmetros otimizados
            payload = {
                "model": "deepseek/deepseek-chat",
                "messages": messages,
                "temperature": 0.3,  # Reduzido para respostas mais consistentes
                "max_tokens": 300,   # Reduzido para respostas mais concisas
                "top_p": 0.9,       # Adicionar controle de qualidade
                "stream": self.use_streaming
            }
            
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://mbsistema.com.br",
                    "X-Title": "MB Sistema - Assistente Virtual",
                },
                json=payload,
                timeout=15,  # Timeout reduzido
                stream=self.use_streaming
            )
            
            if response.status_code == 200:
                if self.use_streaming:
                    self._processar_stream(response)
                else:
                    data = response.json()
                    if 'choices' in data and len(data['choices']) > 0:
                        resposta = data['choices'][0]['message']['content']
                        self.resposta_completa.emit(resposta)
                    else:
                        self.erro_ocorrido.emit("Resposta inválida da API.")
            else:
                self._processar_erro(response)
                
        except requests.exceptions.Timeout:
            self.erro_ocorrido.emit("⏱️ Tempo limite excedido. Tente novamente.")
        except requests.exceptions.ConnectionError:
            self.erro_ocorrido.emit("🌐 Erro de conexão. Verifique sua internet.")
        except Exception as e:
            self.erro_ocorrido.emit(f"❌ Erro: {str(e)}")
    
    def _processar_stream(self, response):
        """Processa resposta em streaming para exibição em tempo real"""
        resposta_completa = ""
        try:
            for line in response.iter_lines():
                if line:
                    line_text = line.decode('utf-8')
                    if line_text.startswith('data: '):
                        json_str = line_text[6:]
                        if json_str.strip() == '[DONE]':
                            break
                        try:
                            data = json.loads(json_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    chunk = delta['content']
                                    resposta_completa += chunk
                                    self.texto_parcial.emit(chunk)
                        except json.JSONDecodeError:
                            continue
            
            self.resposta_completa.emit(resposta_completa)
        except Exception as e:
            self.erro_ocorrido.emit(f"Erro no streaming: {str(e)}")
    
    def _processar_erro(self, response):
        """Processa erros da API de forma simplificada"""
        try:
            error_data = response.json()
            if 'error' in error_data:
                error_msg = error_data['error'].get('message', 'Erro desconhecido')
            else:
                error_msg = f"Erro HTTP {response.status_code}"
        except:
            error_msg = f"Erro HTTP {response.status_code}"
        
        self.erro_ocorrido.emit(f"🚫 {error_msg}")


class MensagemWidget(QFrame):
    """Widget otimizado para mensagens com menos animações"""
    def __init__(self, texto, is_user=False, hora=None):
        super().__init__()
        self.is_user = is_user
        self.setup_ui(texto, hora)
        
    def setup_ui(self, texto, hora):
        """Configuração otimizada da UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(2)
        container_layout.setContentsMargins(0, 0, 0, 0)
        
        self.bolha = QLabel(texto)
        self.bolha.setWordWrap(True)
        self.bolha.setTextFormat(Qt.RichText)
        self.bolha.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.bolha.setMaximumWidth(400)
        
        # Estilos simplificados
        if self.is_user:
            self.bolha.setStyleSheet("""
                QLabel {
                    background-color: #005079;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    font-size: 14px;
                }
            """)
        else:
            self.bolha.setStyleSheet("""
                QLabel {
                    background-color: #2C3E50;
                    color: white;
                    padding: 12px 16px;
                    border-radius: 18px;
                    font-size: 14px;
                }
            """)
        
        container_layout.addWidget(self.bolha)
        
        # Timestamp simplificado
        if hora is None:
            hora = datetime.now().strftime("%H:%M")
        hora_label = QLabel(hora)
        hora_label.setStyleSheet("color: #888; font-size: 11px; padding: 0 5px;")
        hora_label.setAlignment(Qt.AlignRight if self.is_user else Qt.AlignLeft)
        container_layout.addWidget(hora_label)
        
        if self.is_user:
            layout.addStretch(1)
            layout.addWidget(container)
        else:
            layout.addWidget(container)
            layout.addStretch(1)
            
        self.setLayout(layout)
    
    def atualizar_texto(self, novo_texto):
        """Atualiza o texto da mensagem (para streaming)"""
        self.bolha.setText(novo_texto)


class ChatWidget(QWidget):
    """Widget otimizado do chat com streaming"""
    navegar_para = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.historico_conversa = []
        self.api_thread = AssistenteAPI()
        self.mensagens_widgets = []
        self.mensagem_atual_widget = None  # Para streaming
        self.resposta_streaming = ""
        
        # Conectar sinais
        self.api_thread.texto_parcial.connect(self.processar_texto_parcial)
        self.api_thread.resposta_completa.connect(self.processar_resposta_completa)
        self.api_thread.erro_ocorrido.connect(self.processar_erro_api)
        
        self.inicializar_ui()
        QTimer.singleShot(50, self.carregar_historico_otimizado)
        
    def inicializar_ui(self):
        """Interface otimizada"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Área de mensagens otimizada
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea { 
                background-color: #1a1a1a; 
                border: none; 
            }
            QScrollBar:vertical { 
                background-color: #2a2a2a; 
                width: 8px; 
                border-radius: 4px; 
            }
            QScrollBar::handle:vertical { 
                background-color: #555; 
                border-radius: 4px; 
                min-height: 20px;
            }
        """)
        
        self.mensagens_container = QWidget()
        self.mensagens_container.setStyleSheet("background-color: #1a1a1a;")
        self.mensagens_layout = QVBoxLayout(self.mensagens_container)
        self.mensagens_layout.setSpacing(8)
        self.mensagens_layout.setContentsMargins(10, 10, 10, 10)
        self.mensagens_layout.addStretch(1)
        
        self.scroll_area.setWidget(self.mensagens_container)
        layout.addWidget(self.scroll_area, 1)
        
        # Área de input otimizada
        input_container = QFrame()
        input_container.setStyleSheet("""
            QFrame { 
                background-color: #272525; 
                padding: 10px; 
                border-top: 1px solid #333; 
                min-height: 60px; 
                max-height: 60px;
            }
        """)
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(10)
        
        self.entrada_texto = QLineEdit()
        self.entrada_texto.setPlaceholderText("Digite sua mensagem...")
        self.entrada_texto.setStyleSheet("""
            QLineEdit { 
                padding: 12px 20px; 
                border: 2px solid #444; 
                border-radius: 25px; 
                font-size: 14px; 
                background-color: #1a1a1a; 
                color: white;
            }
            QLineEdit:focus { 
                border-color: #005079; 
            }
        """)
        self.entrada_texto.returnPressed.connect(self.processar_mensagem)
        
        self.btn_enviar = QPushButton("➤")
        self.btn_enviar.setFixedSize(40, 40)
        self.btn_enviar.setStyleSheet("""
            QPushButton { 
                background-color: #005079; 
                color: white; 
                border: none; 
                border-radius: 20px; 
                font-size: 18px;
            }
            QPushButton:hover { 
                background-color: #0066a0; 
            }
            QPushButton:disabled { 
                background-color: #003d5c; 
            }
        """)
        self.btn_enviar.clicked.connect(self.processar_mensagem)
        
        input_layout.addWidget(self.entrada_texto)
        input_layout.addWidget(self.btn_enviar)
        layout.addWidget(input_container)
        
        # Sugestões otimizadas
        self.criar_sugestoes(layout)

    def criar_sugestoes(self, layout):
        """Cria área de sugestões otimizada"""
        sugestoes_frame = QFrame()
        sugestoes_frame.setStyleSheet("""
            QFrame { 
                background-color: #1a1a1a; 
                padding: 8px; 
                max-height: 45px;
            }
        """)
        sugestoes_layout = QHBoxLayout(sugestoes_frame)
        sugestoes_layout.setSpacing(8)
        sugestoes_layout.setContentsMargins(5, 0, 5, 0)
        
        # Sugestões atualizadas com consultas de dados
        sugestoes = ["Quantos clientes tenho?", "Resumo geral", "Abrir PDV", "Produtos estoque baixo"]
        for sugestao in sugestoes:
            btn = QPushButton(sugestao)
            btn.setStyleSheet("""
                QPushButton { 
                    background-color: #2C3E50; 
                    color: white; 
                    border: none; 
                    padding: 6px 12px; 
                    border-radius: 15px; 
                    font-size: 12px;
                }
                QPushButton:hover { 
                    background-color: #34495E; 
                }
            """)
            btn.clicked.connect(lambda checked, s=sugestao: self.usar_sugestao(s))
            sugestoes_layout.addWidget(btn)
            
        sugestoes_layout.addStretch()
        layout.addWidget(sugestoes_frame)

    def usar_sugestao(self, texto):
        """Usar sugestão otimizada"""
        self.entrada_texto.setText(texto)
        self.processar_mensagem()

    def processar_mensagem(self):
        """Processamento otimizado de mensagens"""
        mensagem = self.entrada_texto.text().strip()
        if not mensagem or self.api_thread.isRunning():
            return
            
        self.adicionar_mensagem_usuario(mensagem)
        self.entrada_texto.clear()
        self.btn_enviar.setEnabled(False)
        self.entrada_texto.setEnabled(False)
        
        # Preparar para streaming
        self.resposta_streaming = ""
        self.mensagem_atual_widget = self.adicionar_mensagem_bot("", streaming=True)
        
        self.api_thread.configurar_mensagem(mensagem, self.historico_conversa, use_streaming=True)
        self.api_thread.start()

    def adicionar_mensagem_usuario(self, texto):
        """Adiciona mensagem do usuário otimizada"""
        mensagem_widget = MensagemWidget(texto, is_user=True)
        self.mensagens_layout.insertWidget(self.mensagens_layout.count() - 1, mensagem_widget)
        self.mensagens_widgets.append(mensagem_widget)
        self.historico_conversa.append({"role": "user", "content": texto})
        QTimer.singleShot(10, self.rolar_para_fim)
        
    def adicionar_mensagem_bot(self, texto, streaming=False):
        """Adiciona mensagem do bot otimizada"""
        if streaming and not texto:
            texto = "💭 Pensando..."
            
        texto_html = texto.replace('\n', '<br>')
        mensagem_widget = MensagemWidget(texto_html, is_user=False)
        self.mensagens_layout.insertWidget(self.mensagens_layout.count() - 1, mensagem_widget)
        self.mensagens_widgets.append(mensagem_widget)
        QTimer.singleShot(10, self.rolar_para_fim)
        return mensagem_widget

    @pyqtSlot(str)
    def processar_texto_parcial(self, chunk):
        """Processa texto parcial do streaming"""
        self.resposta_streaming += chunk
        if self.mensagem_atual_widget:
            texto_formatado = self.resposta_streaming.replace('\n', '<br>')
            self.mensagem_atual_widget.atualizar_texto(texto_formatado)
            QTimer.singleShot(5, self.rolar_para_fim)

    @pyqtSlot(str)
    def processar_resposta_completa(self, resposta_completa):
        """Processa resposta completa"""
        if resposta_completa and resposta_completa != self.resposta_streaming:
            # Usar resposta completa se diferente do streaming
            self.resposta_streaming = resposta_completa
            if self.mensagem_atual_widget:
                texto_formatado = resposta_completa.replace('\n', '<br>')
                self.mensagem_atual_widget.atualizar_texto(texto_formatado)
        
        self.historico_conversa.append({"role": "assistant", "content": self.resposta_streaming})
        self.salvar_historico_otimizado()
        self.finalizar_interacao()
        self.processar_comandos_navegacao(self.resposta_streaming)

    @pyqtSlot(str)
    def processar_erro_api(self, erro):
        """Processa erros otimizado"""
        if self.mensagem_atual_widget:
            self.mensagem_atual_widget.atualizar_texto(f"❌ {erro}")
        else:
            self.adicionar_mensagem_bot(f"❌ {erro}")
        self.finalizar_interacao()

    def finalizar_interacao(self):
        """Finaliza interação e reabilita controles"""
        self.mensagem_atual_widget = None
        self.resposta_streaming = ""
        self.btn_enviar.setEnabled(True)
        self.entrada_texto.setEnabled(True)
        self.entrada_texto.setFocus()

    def rolar_para_fim(self):
        """Rolagem otimizada"""
        scrollbar = self.scroll_area.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def processar_comandos_navegacao(self, resposta):
        """Detecção otimizada de comandos de navegação"""
        navegacao = {
            "cadastro de cliente": ("geral", "cadastro_pessoa"),
            "cadastrar cliente": ("geral", "cadastro_pessoa"),
            "pdv": ("pdv", "pdv_principal"),
            "ponto de venda": ("pdv", "pdv_principal"),
            "relatório": ("relatorios", "relatorio_vendas_produtos"),
        }
        
        resposta_lower = resposta.lower()
        for palavra_chave, (modulo, acao) in navegacao.items():
            if palavra_chave in resposta_lower:
                self.navegar_para.emit(modulo, acao)
                break

    def carregar_historico_otimizado(self):
        """Carregamento otimizado do histórico"""
        try:
            historico_path = self.get_historico_path()
            if os.path.exists(historico_path):
                with open(historico_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Carregar apenas últimas 10 mensagens
                    historico_completo = data.get("conversas", [])
                    self.historico_conversa = historico_completo[-20:]  # Manter mais no histórico
                    historico_para_exibir = historico_completo[-10:]   # Exibir menos
                    
                for msg in historico_para_exibir:
                    texto = msg.get('content', '')
                    if msg.get('role') == 'user':
                        self.adicionar_mensagem_usuario_historico(texto)
                    elif msg.get('role') == 'assistant':
                        self.adicionar_mensagem_bot(texto)
                        
                if historico_para_exibir:
                    QTimer.singleShot(50, self.rolar_para_fim)
                else:
                    self.mensagem_boas_vindas()
            else:
                self.mensagem_boas_vindas()
        except Exception as e:
            print(f"Erro ao carregar histórico: {e}")
            self.mensagem_boas_vindas()

    def adicionar_mensagem_usuario_historico(self, texto):
        """Adiciona mensagem do usuário do histórico sem duplicar no array"""
        mensagem_widget = MensagemWidget(texto, is_user=True)
        self.mensagens_layout.insertWidget(self.mensagens_layout.count() - 1, mensagem_widget)
        self.mensagens_widgets.append(mensagem_widget)

    def mensagem_boas_vindas(self):
        """Mensagem de boas-vindas otimizada"""
        self.adicionar_mensagem_bot(
            "👋 **Olá! Sou seu assistente do MB Sistema!**\n\n"
            "Posso ajudá-lo a:\n"
            "• Navegar pelo sistema\n"
            "• Encontrar módulos específicos\n"
            "• **Consultar dados do sistema**\n"
            "• Explicar funcionalidades\n\n"
            "**Experimente perguntar:**\n"
            "• Quantos clientes tenho?\n"
            "• Resumo geral do sistema\n"
            "• Produtos com estoque baixo\n\n"
            "Como posso ajudá-lo hoje?"
        )

    def get_historico_path(self):
        """Caminho do histórico"""
        if getattr(sys, 'frozen', False):
            app_path = os.path.dirname(sys.executable)
        else:
            app_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(app_path, "assistente_historico.json")

    def salvar_historico_otimizado(self):
        """Salvamento otimizado do histórico"""
        try:
            historico_path = self.get_historico_path()
            # Salvar apenas últimas 30 mensagens
            historico_salvar = self.historico_conversa[-30:]
            with open(historico_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "ultima_atualizacao": datetime.now().isoformat(),
                    "conversas": historico_salvar
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao salvar histórico: {e}")

    def limpar_historico(self):
        """Limpeza otimizada do histórico"""
        resposta = QMessageBox.question(
            self, "Limpar Conversa", 
            "Deseja limpar o histórico da conversa?",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if resposta == QMessageBox.Yes:
            # Limpar widgets
            while self.mensagens_layout.count() > 1:
                item = self.mensagens_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
            self.mensagens_widgets.clear()
            self.historico_conversa = []
            self.salvar_historico_otimizado()
            self.mensagem_boas_vindas()


class ChatbotAssistente(QWidget):
    """Widget principal otimizado"""
    navegar_para = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.inicializar_ui()
        
    def inicializar_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header otimizado
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame { 
                background-color: #005079; 
                min-height: 40px; 
                max-height: 40px;
            }
        """)
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 5, 10, 5)
        
        header = QLabel("🤖 Assistente MB")
        header.setStyleSheet("""
            QLabel { 
                color: white; 
                font-size: 16px; 
                font-weight: bold;
            }
        """)
        header_layout.addWidget(header, 1)
        
        btn_limpar = QPushButton("🗑️")
        btn_limpar.setToolTip("Limpar conversa")
        btn_limpar.setFixedSize(30, 30)
        btn_limpar.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: white; 
                border: none; 
                font-size: 16px; 
                border-radius: 15px;
            }
            QPushButton:hover { 
                background-color: rgba(255, 255, 255, 0.2);
            }
        """)
        header_layout.addWidget(btn_limpar)
        layout.addWidget(header_frame)
        
        self.chat_widget = ChatWidget()
        btn_limpar.clicked.connect(self.chat_widget.limpar_historico)
        self.chat_widget.navegar_para.connect(self.navegar_para)
        layout.addWidget(self.chat_widget, 1)


class ChatbotDockWidget(QDockWidget):
    """Dock widget otimizado"""
    navegar_para_main = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        super().__init__("Assistente Virtual", parent)
        self.chatbot_widget_interno = ChatbotAssistente()
        self.setWidget(self.chatbot_widget_interno)
        self.chatbot_widget_interno.navegar_para.connect(self.navegar_para_main.emit)
        
        # Configurações otimizadas
        self.setFeatures(
            QDockWidget.DockWidgetMovable | 
            QDockWidget.DockWidgetFloatable | 
            QDockWidget.DockWidgetClosable
        )
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setMinimumWidth(350)
        self.setMaximumWidth(500)
        
        self.setStyleSheet("""
            QDockWidget { 
                border: 1px solid #005079;
            }
            QDockWidget::title { 
                background-color: #005079; 
                color: white; 
                padding: 8px; 
                font-weight: bold;
            }
        """)


# Função de integração otimizada
def adicionar_assistente_ao_sistema(main_window):
    """Adiciona assistente otimizado ao sistema"""
    if hasattr(main_window, 'chatbot_dock') and main_window.chatbot_dock is not None:
        return

    # Botão otimizado
    main_window.btn_assistente = QPushButton("💬", main_window)
    main_window.btn_assistente.setFixedSize(60, 60)
    main_window.btn_assistente.setStyleSheet("""
        QPushButton { 
            background-color: #005079; 
            color: white; 
            border: 2px solid white; 
            border-radius: 30px; 
            font-size: 24px;
        }
        QPushButton:hover { 
            background-color: #0066a0;
        }
    """)
    
    main_window.btn_assistente.setToolTip("Assistente Virtual")
    main_window.chatbot_dock = ChatbotDockWidget(main_window)
    main_window.addDockWidget(Qt.RightDockWidgetArea, main_window.chatbot_dock)
    main_window.chatbot_dock.hide()
    
    # Conectar sinais
    main_window.chatbot_dock.navegar_para_main.connect(
        lambda m, a: navegar_para_modulo(main_window, m, a)
    )
    main_window.btn_assistente.clicked.connect(
        lambda: toggle_assistente(main_window)
    )
    
    # Posicionamento otimizado
    def posicionar_botao():
        if hasattr(main_window, 'btn_assistente'):
            offset_y = 30
            if hasattr(main_window, 'botao_whatsapp') and main_window.botao_whatsapp.isVisible():
                offset_y += main_window.botao_whatsapp.height() + 15
                
            main_window.btn_assistente.move(
                main_window.width() - main_window.btn_assistente.width() - 30,
                main_window.height() - main_window.btn_assistente.height() - offset_y
            )
            main_window.btn_assistente.raise_()
    
    # Override do resize event
    original_resize = getattr(main_window, 'resizeEvent', None)
    def novo_resize_event(event):
        if original_resize:
            original_resize(event)
        posicionar_botao()
    
    main_window.resizeEvent = novo_resize_event
    QTimer.singleShot(0, posicionar_botao)


def toggle_assistente(main_window):
    """Toggle otimizado do assistente"""
    if not hasattr(main_window, 'chatbot_dock'):
        return
        
    if main_window.chatbot_dock.isVisible():
        main_window.chatbot_dock.hide()
    else:
        main_window.chatbot_dock.show()
        QTimer.singleShot(100, lambda: 
            main_window.chatbot_dock.chatbot_widget_interno.chat_widget.entrada_texto.setFocus()
        )


def navegar_para_modulo(main_window, modulo, acao):
    """Navegação otimizada para módulos"""
    mapa_navegacao = {
        ("geral", "cadastro_pessoa"): "Cadastro de Clientes",
        ("pdv", "pdv_principal"): "PDV - Ponto de Venda",
        ("relatorios", "relatorio_vendas_produtos"): "Relatório de Vendas de Produtos",
    }
    
    chave = (str(modulo).lower(), str(acao).lower())
    action_title = mapa_navegacao.get(chave)
    
    if action_title and hasattr(main_window, 'menu_action_triggered'):
        main_window.menu_action_triggered(action_title)
    elif chave == ("pdv", "pdv_principal") and hasattr(main_window, 'abrir_pdv'):
        main_window.abrir_pdv()