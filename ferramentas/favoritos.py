import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QFrame, QGraphicsDropShadowEffect, QScrollArea, 
    QCheckBox, QListWidget, QPushButton, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QCursor
from PyQt5.QtCore import Qt

# --- NOVO: Importar o necessário para acessar o banco de dados ---
# Certifique-se de que o caminho para 'base' está correto no seu projeto
try:
    from base.banco import execute_query
except ImportError:
    # Adiciona o diretório pai ao path se o import direto falhar
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from base.banco import execute_query

class SeletorModulosEstilizado(QDialog):
    """
    Uma janela de diálogo com estilo para selecionar módulos favoritos.
    Esta classe agora herda de QDialog para se integrar com a janela principal.
    """
    # --- MODIFICADO: Adicionado 'usuario_id' ao construtor ---
    def __init__(self, modulos_disponiveis, favoritos_atuais, usuario_id, parent=None):
        super().__init__(parent)
        
        # Recebe os módulos e favoritos da tela principal
        self.modulos_disponiveis = sorted(list(modulos_disponiveis))
        self.favoritos_atuais = favoritos_atuais
        
        # --- NOVO: Armazena o ID do usuário logado ---
        self.usuario_id = usuario_id
        # --- NOVO: Define o nome exato do módulo a ser verificado ---
        self.modulo_ecommerce_nome = "Ver Dashboard do Mercado livre" # <-- ATENÇÃO: Verifique se este nome corresponde exatamente ao da sua lista
        
        # --- NOVO: Lista de módulos que exigem permissão especial ---
        self.modulos_com_restricao = {
            "Ver Dashboard do Mercado livre": "ACESSO_ECOMMERCE",
            "Dashboard Mercado Livre": "ACESSO_ECOMMERCE"
        }
        
        self.initUI()
        self.setWindowTitle("Gerenciar Módulos Favoritos")
        
        # Preenche a lista da direita com os favoritos que já estavam selecionados
        # --- MODIFICADO: Agora filtra módulos sem permissão ---
        self.atualizar_lista_favoritos()

    def initUI(self):
        """
        Inicializa a interface do usuário com o estilo profissional.
        """
        self.setMinimumSize(900, 700)
        self.setModal(True)
        
        self.setStyleSheet("background-color: #0a3b59;")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        title_label = QLabel("Adicionar ou Remover Módulos Favoritos")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        content_container = QFrame()
        content_container.setStyleSheet("background-color: #0a3b59; border-radius: 10px;")
        
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(5, 5)
        content_container.setGraphicsEffect(shadow)
        
        sections_layout = QHBoxLayout(content_container)
        sections_layout.setSpacing(20)
        sections_layout.setContentsMargins(20, 20, 20, 20)
        
        modulos_frame = QFrame()
        modulos_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        modulos_layout = QVBoxLayout(modulos_frame)
        
        modulos_label = QLabel("Módulos Disponíveis")
        modulos_label.setFont(QFont("Arial", 14, QFont.Bold))
        modulos_layout.addWidget(modulos_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("background-color: white; border: none;")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setAlignment(Qt.AlignTop)

        self.checkboxes = []
        for modulo_nome in self.modulos_disponiveis:
            checkbox = QCheckBox(modulo_nome)
            checkbox.setFont(QFont("Arial", 12))
            
            # --- NOVO: Verifica se o módulo tem restrição e se o usuário tem permissão ---
            if modulo_nome in self.modulos_com_restricao:
                if not self.verificar_permissao_modulo(modulo_nome):
                    # Se não tem permissão, desabilita o checkbox e muda a cor
                    checkbox.setEnabled(False)
                    checkbox.setStyleSheet("color: #888888; font-style: italic;")
                    checkbox.setText(f"{modulo_nome} (Acesso Bloqueado)")
            
            # --- MODIFICADO: Só marca como selecionado se estiver nos favoritos E tiver permissão ---
            if modulo_nome in self.favoritos_atuais and checkbox.isEnabled():
                checkbox.setChecked(True)
                
            # --- MODIFICADO: Conectado a um novo método ---
            checkbox.stateChanged.connect(self.on_checkbox_changed)
            scroll_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
        
        scroll_area.setWidget(scroll_content)
        modulos_layout.addWidget(scroll_area)
        sections_layout.addWidget(modulos_frame, 1)
        
        principal_frame = QFrame()
        principal_frame.setStyleSheet("background-color: white; border-radius: 5px;")
        principal_layout = QVBoxLayout(principal_frame)
        
        principal_label = QLabel("Favoritos Selecionados")
        principal_label.setFont(QFont("Arial", 14, QFont.Bold))
        principal_layout.addWidget(principal_label)
        
        self.lista_tela_principal = QListWidget()
        self.lista_tela_principal.setStyleSheet("background-color: white; border: none; font-size: 12pt;")
        principal_layout.addWidget(self.lista_tela_principal)
        sections_layout.addWidget(principal_frame, 1)
        
        main_layout.addWidget(content_container)

        confirm_button = QPushButton("Confirmar")
        confirm_button.setFont(QFont("Arial", 12, QFont.Bold))
        confirm_button.setCursor(QCursor(Qt.PointingHandCursor))
        confirm_button.setStyleSheet("""
            QPushButton { background-color: #00e676; color: white; border-radius: 5px; padding: 10px; border: none; }
            QPushButton:hover { background-color: #00c853; }
            QPushButton:pressed { background-color: #00b248; }
        """)
        confirm_button.clicked.connect(self.confirmar_selecao)
        main_layout.addWidget(confirm_button)

    # --- NOVO: Função para verificar permissão de um módulo específico ---
    def verificar_permissao_modulo(self, nome_modulo):
        """
        Verifica se o usuário tem permissão para acessar um módulo específico.
        """
        if nome_modulo not in self.modulos_com_restricao:
            return True  # Se o módulo não tem restrição, permite acesso
            
        campo_permissao = self.modulos_com_restricao[nome_modulo]
        
        if self.usuario_id is None:
            return False  # Se não houver ID de usuário, nega por segurança

        try:
            # 1. Descobrir se o usuário é master ou funcionário
            query_user_info = f"SELECT USUARIO_MASTER FROM USUARIOS WHERE ID = {self.usuario_id}"
            result = execute_query(query_user_info)
            
            if not result or not result[0]:
                print(f"Aviso: Usuário com ID {self.usuario_id} não encontrado no banco.")
                return False

            usuario_master_id = result[0][0]
            
            # Se o usuário não tem um mestre (é NULL), ele é o próprio mestre.
            id_para_verificar = usuario_master_id if usuario_master_id is not None else self.usuario_id

            # 2. Verificar a permissão específica do usuário mestre
            query_permissao = f"SELECT {campo_permissao} FROM USUARIOS WHERE ID = {id_para_verificar}"
            permissao_result = execute_query(query_permissao)

            if permissao_result and permissao_result[0] and permissao_result[0][0] == 'S':
                return True  # Acesso permitido
            else:
                return False  # Acesso negado

        except Exception as e:
            print(f"Erro ao verificar permissão para módulo {nome_modulo}: {e}")
            return False  # Em caso de erro, nega o acesso por segurança

    # --- MODIFICADO: Método para gerenciar as mudanças nos checkboxes ---
    def on_checkbox_changed(self, state):
        """
        Chamado sempre que um checkbox muda de estado.
        Verifica permissões e limites antes de atualizar a lista.
        """
        sender = self.sender()
        if not sender:
            return

        # Verifica se o usuário está TENTANDO ADICIONAR (marcando a caixa)
        if state == Qt.Checked:
            # Obtém o nome do módulo (remove o sufixo " (Acesso Bloqueado)" se existir)
            nome_modulo = sender.text().replace(" (Acesso Bloqueado)", "")
            
            # Verifica se é um módulo com restrição
            if nome_modulo in self.modulos_com_restricao:
                # Se for, verifica a permissão
                if not self.verificar_permissao_modulo(nome_modulo):
                    # Bloqueia sinais para evitar loop
                    sender.blockSignals(True)
                    # Desmarca a caixa
                    sender.setChecked(False)
                    # Reativa sinais
                    sender.blockSignals(False)
                    # Mostra a mensagem de bloqueio
                    QMessageBox.warning(self, "Acesso Bloqueado", 
                                        f"Seu usuário não tem permissão para acessar o módulo: {nome_modulo}.\n\n"
                                        "Entre em contato com o administrador da sua empresa para liberar o acesso.")
                    return  # Para a execução aqui

        # Se passou na verificação (ou não era um módulo restrito), atualiza a lista
        self.atualizar_lista_favoritos()

    def atualizar_lista_favoritos(self):
        """
        Atualiza a lista de módulos selecionados, filtra módulos sem permissão
        e impõe um limite de 6 seleções.
        """
        modulos_selecionados = []
        for checkbox in self.checkboxes:
            if checkbox.isChecked() and checkbox.isEnabled():
                # Remove o sufixo " (Acesso Bloqueado)" se existir
                nome_modulo = checkbox.text().replace(" (Acesso Bloqueado)", "")
                modulos_selecionados.append(nome_modulo)

        # Lógica para limitar a seleção a 6 módulos
        if len(modulos_selecionados) > 6:
            sender = self.sender()
            if sender:
                sender.blockSignals(True)
                sender.setChecked(False)  # Desmarca o que excedeu
                sender.blockSignals(False)
            
            QMessageBox.warning(self, "Limite Atingido", "Você pode selecionar no máximo 6 módulos favoritos.")
            modulos_selecionados.pop()  # Remove o item excedente da lista lógica

        # Atualiza a lista da direita (visual)
        self.lista_tela_principal.clear()
        self.lista_tela_principal.addItems(sorted(modulos_selecionados))

    def confirmar_selecao(self):
        self.accept()

    def get_selecao_final(self):
        """
        Retorna apenas módulos que o usuário tem permissão para acessar.
        """
        modulos_selecionados = []
        for i in range(self.lista_tela_principal.count()):
            nome_modulo = self.lista_tela_principal.item(i).text()
            # Dupla verificação: só adiciona se tiver permissão
            if nome_modulo not in self.modulos_com_restricao or self.verificar_permissao_modulo(nome_modulo):
                modulos_selecionados.append(nome_modulo)
        return modulos_selecionados

    # --- NOVO: Método para filtrar favoritos existentes ---
    def filtrar_favoritos_com_permissao(self, favoritos_lista):
        """
        Filtra uma lista de favoritos, removendo aqueles para os quais
        o usuário não tem permissão.
        """
        favoritos_permitidos = []
        for modulo in favoritos_lista:
            if modulo not in self.modulos_com_restricao or self.verificar_permissao_modulo(modulo):
                favoritos_permitidos.append(modulo)
            else:
                print(f"Módulo '{modulo}' removido dos favoritos: sem permissão de acesso.")
        return favoritos_permitidos


if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # Simula os dados que viriam da tela principal
    modulos_teste = [
        "Cadastro de Clientes", "Produtos", "Pedido de vendas", 
        "Controle de caixa (PDV)", "Consulta CNPJ", "Fornecedores",
        "Ver Dashboard do Mercado livre"  # Módulo que será bloqueado se não tiver permissão
    ]
    favoritos_teste = ["Produtos", "Cadastro de Clientes", "Ver Dashboard do Mercado livre"]
    
    # --- NOVO: Simula o ID do usuário logado ---
    # Altere este valor para testar diferentes cenários.
    # Use um ID de usuário que você saiba que TEM ou NÃO TEM a permissão 'S' no seu banco.
    id_usuario_logado_para_teste = 1  # Substitua pelo ID de um usuário real do seu banco para testar
    
    janela = SeletorModulosEstilizado(
        modulos_disponiveis=modulos_teste, 
        favoritos_atuais=favoritos_teste,
        usuario_id=id_usuario_logado_para_teste  # Passando o ID
    )
    
    resultado = janela.exec_()
    if resultado == QDialog.Accepted:
        print("Seleção confirmada!")
        selecao = janela.get_selecao_final()
        print("Favoritos escolhidos:", selecao)
    else:
        print("Seleção cancelada.")
        
    sys.exit(0)