from PyQt5.QtWidgets import (
    QMainWindow, QLabel, QLineEdit, QDateEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox, QInputDialog,
    QHeaderView, QGroupBox, QSpacerItem, QSizePolicy, QStatusBar, QAbstractItemView
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont
import firebird.driver as fdb
import os
from datetime import datetime, date, time
import sys # Importar sys
from financeiro.paths import get_app_base_path


class ControleCaixaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.usuario = None
        self.empresa = None
        self.id_funcionario = None
        self.conexao = None

        self.setWindowTitle("Controle de Caixa (PDV)")
        # Diminuindo o tamanho da janela
        self.resize(800, 500)

        # Fonte padrão
        default_font = QFont("Segoe UI", 10)
        self.setFont(default_font)

        # Paleta e estilo global — mantendo texto branco nas células e CABEÇALHO em preto
        self.setStyleSheet("""
            QMainWindow { background-color: #005079; color: white; }
            QLabel, QGroupBox, QLineEdit, QDateEdit, QPushButton, QTableWidget, QStatusBar {
                color: white;
            }
            QLabel#title { font-size: 26px; font-weight: 700; margin: 8px 0 12px 0; }
            QGroupBox { 
                border: 1px solid rgba(255,255,255,0.08); 
                border-radius: 8px; 
                margin-top: 6px;
                padding: 8px;
                color: white;
            }
            QGroupBox::title { subcontrol-origin: margin; left: 8px; padding: 0 4px; }
            QLineEdit, QDateEdit {
                background: rgba(255,255,255,0.06);
                border: 1px solid rgba(255,255,255,0.12);
                border-radius: 6px;
                padding: 6px;
                color: white;
            }
            QLineEdit::placeholder { color: rgba(255,255,255,0.6); }
            QTableWidget {
                background-color: #00455f;
                alternate-background-color: #003a50;
                color: white; /* células: texto branco sobre fundo escuro */
                border: 1px solid rgba(0,0,0,0.15);
                gridline-color: rgba(255,255,255,0.04);
                selection-background-color: rgba(255,255,255,0.12);
            }
            QTableWidget QTableCornerButton { background: rgba(0,0,0,0.06); color: white; }
            /* Cabeçalho com fundo claro e texto preto para contraste */
            QHeaderView::section {
                background-color: #f3f3f3;
                padding: 6px;
                border: none;
                font-weight: 600;
                color: black;
            }
            QPushButton {
                background-color: #003b58;
                border-radius: 6px;
                padding: 8px 14px;
                min-height: 32px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover { background-color: #002f44; }
            QPushButton:pressed { background-color: #001f2a; }
            QStatusBar { background: transparent; color: white; }

            QMessageBox {
                background-color: #ffffff;
                color: #000000;
                border-radius: 8px;
            }
            QMessageBox QLabel, QMessageBox QLabel#qt_msgbox_label {
                color: #000000;
            }
            QMessageBox QPushButton {
                background-color: #003b58;
                color: white;
                border-radius: 6px;
                padding: 6px 12px;
            }
            QMessageBox QPushButton:hover { background-color: #002f44; }
        """)

        # Configuração da conexão com banco
        self.configurar_banco()

        # Montar UI
        self._montar_ui()

        # Criar tabela e carregar dados
        self.criar_tabela_se_necessario()
        self.carregar_dados()

    def _montar_ui(self):
        central = QWidget(self)
        self.setCentralWidget(central)

        # ---------- Campos de filtro ----------
        self.edit_data_inicial = QDateEdit(self)
        self.edit_data_inicial.setCalendarPopup(True)
        self.edit_data_inicial.setDate(QDate.currentDate())

        self.edit_data_final = QDateEdit(self)
        self.edit_data_final.setCalendarPopup(True)
        self.edit_data_final.setDate(QDate.currentDate())

        # Campos de filtro que estavam sendo usados no código
        self.codigo_edit = QLineEdit(self)
        self.codigo_edit.setPlaceholderText("Código do Caixa")

        self.usuario_edit = QLineEdit(self)
        self.usuario_edit.setPlaceholderText("Usuário")

        # Renomear os campos de data para corresponder ao código
        self.data_inicio = self.edit_data_inicial
        self.data_fim = self.edit_data_final

        self.btn_filtrar = QPushButton("Filtrar", self)
        self.btn_filtrar.clicked.connect(self.filtrar_registros)

        # Layout de filtros
        filtros_layout = QHBoxLayout()
        filtros_layout.addWidget(QLabel("Código:"))
        filtros_layout.addWidget(self.codigo_edit)
        filtros_layout.addWidget(QLabel("Usuário:"))
        filtros_layout.addWidget(self.usuario_edit)
        filtros_layout.addWidget(QLabel("Data Inicial:"))
        filtros_layout.addWidget(self.edit_data_inicial)
        filtros_layout.addWidget(QLabel("Data Final:"))
        filtros_layout.addWidget(self.edit_data_final)
        filtros_layout.addWidget(self.btn_filtrar)
        filtros_layout.addStretch(1)

        # ---------- Tabela ----------
        self.tabela = QTableWidget(self)
        self.tabela.setColumnCount(6)
        self.tabela.setHorizontalHeaderLabels([
            "Código", "Data Abertura", "Hora Abertura", "Data Fechamento", "Hora Fechamento", "Usuário"
        ])
        self.tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Criar referência para self.table (usado no código original)
        self.table = self.tabela

        # ---------- Botões inferiores (REMOVIDOS Excluir e Atualizar) ----------
        self.btn_incluir = QPushButton("Abrir Caixa", self)
        self.btn_incluir.clicked.connect(self.abrir_caixa)
        
        self.btn_editar = QPushButton("Fechar Caixa", self)
        self.btn_editar.clicked.connect(self.fechar_caixa)

        # Layout dos botões - apenas com Abrir e Fechar Caixa
        botoes_layout = QHBoxLayout()
        botoes_layout.addWidget(self.btn_incluir)
        botoes_layout.addWidget(self.btn_editar)
        botoes_layout.addStretch(1)  # Empurra os botões para a esquerda

        # ---------- Status Bar ----------
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # ---------- Layout principal ----------
        main_layout = QVBoxLayout()
        main_layout.addLayout(filtros_layout)
        main_layout.addWidget(self.tabela)
        main_layout.addLayout(botoes_layout)

        central.setLayout(main_layout)

    def filtrar_registros(self):
        """Aplica os filtros e recarrega os dados"""
        self.carregar_dados()

    def carregar_dados(self):
        """Carrega os dados da tabela CAIXA com filtros dinâmicos"""
        if not self.conexao:
            QMessageBox.warning(self, "Erro", "Sem conexão com banco de dados!")
            return

        try:
            cursor = self.conexao.cursor()

            sql = """
                SELECT CODIGO, DATA_ABERTURA, HORA_ABERTURA,
                    DATA_FECHAMENTO, HORA_FECHAMENTO, USUARIO
                FROM CAIXA
                WHERE 1=1
            """
            params = []

            # Filtros dinâmicos
            codigo_texto = self.codigo_edit.text().strip()
            if codigo_texto:
                try:
                    codigo = int(codigo_texto)
                    sql += " AND CODIGO = ?"
                    params.append(codigo)
                except ValueError:
                    QMessageBox.warning(self, "Erro", "O código deve ser um número inteiro.")
                    return

            usuario_texto = self.usuario_edit.text().strip()
            if usuario_texto:
                sql += " AND UPPER(USUARIO) LIKE UPPER(?)"
                params.append(f"%{usuario_texto}%")

            # Só filtra se realmente tiver datas válidas
            if self.data_inicio.date().isValid() and self.data_fim.date().isValid():
                inicio = self.data_inicio.date().toPyDate()
                fim = self.data_fim.date().toPyDate()
                sql += " AND DATA_ABERTURA BETWEEN ? AND ?"
                params.extend([inicio, fim])
            elif self.data_inicio.date().isValid():
                inicio = self.data_inicio.date().toPyDate()
                sql += " AND DATA_ABERTURA >= ?"
                params.append(inicio)
            elif self.data_fim.date().isValid():
                fim = self.data_fim.date().toPyDate()
                sql += " AND DATA_ABERTURA <= ?"
                params.append(fim)

            sql += " ORDER BY DATA_ABERTURA DESC, HORA_ABERTURA DESC"

            print(f"SQL: {sql}")
            print(f"Params: {params}")

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Limpa a tabela
            self.table.setRowCount(0)

            # Preenche a tabela
            self.table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    if value is None:
                        item_text = ""
                    elif isinstance(value, date):
                        item_text = value.strftime("%d/%m/%Y")
                    elif isinstance(value, time):
                        item_text = value.strftime("%H:%M:%S")
                    else:
                        item_text = str(value)

                    item = QTableWidgetItem(item_text)
                    item.setTextAlignment(Qt.AlignCenter if j in [0, 1, 2, 3, 4] else Qt.AlignLeft)
                    item.setForeground(Qt.white)
                    self.table.setItem(i, j, item)

            cursor.close()
            self.update_status(len(rows))
            print(f"✅ Carregados {len(rows)} registros")

        except Exception as e:
            print(f"❌ Erro ao carregar dados: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao carregar dados:\n{e}")
            self.update_status(0)

    def criar_tabela_se_necessario(self):
        """Cria a tabela CAIXA se ela não existir"""
        if not self.conexao:
            return
            
        try:
            cursor = self.conexao.cursor()
            
            # Verifica se a tabela existe
            cursor.execute("""
                SELECT COUNT(*) FROM RDB$RELATIONS 
                WHERE RDB$RELATION_NAME = 'CAIXA' AND RDB$SYSTEM_FLAG = 0
            """)
            
            if cursor.fetchone()[0] == 0:
                print("Tabela CAIXA não existe. Criando...")
                
                # Cria a tabela
                cursor.execute("""
                    CREATE TABLE CAIXA (
                        CODIGO INTEGER NOT NULL PRIMARY KEY,
                        DATA_ABERTURA DATE,
                        HORA_ABERTURA TIME,
                        DATA_FECHAMENTO DATE,
                        HORA_FECHAMENTO TIME,
                        USUARIO VARCHAR(50),
                        FUNDO_TROCO DECIMAL(10,2) DEFAULT 0.00,
                        STATUS VARCHAR(10) DEFAULT 'ABERTO'
                    )
                """)
                
                # Cria sequence para auto incremento
                cursor.execute("CREATE SEQUENCE SEQ_CAIXA")
                
                # Cria trigger para auto incremento
                cursor.execute("""
                    CREATE TRIGGER TRG_CAIXA_BI FOR CAIXA
                    ACTIVE BEFORE INSERT POSITION 0
                    AS
                    BEGIN
                        IF (NEW.CODIGO IS NULL) THEN
                            NEW.CODIGO = NEXT VALUE FOR SEQ_CAIXA;
                    END
                """)
                
                self.conexao.commit()
                print("✅ Tabela CAIXA criada com sucesso!")
                
            cursor.close()
            
        except Exception as e:
            print(f"❌ Erro ao criar tabela: {e}")
            if self.conexao:
                self.conexao.rollback()

    def update_status(self, total):
        self.status.showMessage(f"Total de registros: {total}")

    def set_credentials(self, usuario, empresa, id_funcionario):
        """Define as credenciais do usuário"""
        self.usuario = usuario
        self.empresa = empresa
        self.id_funcionario = id_funcionario

    def configurar_banco(self):
        """Configura conexão com banco Firebird"""
        try:
            app_base_path = get_app_base_path()
            db_path = os.path.join(app_base_path, "base", "banco", "MBDATA_NOVO.FDB")
            print(f"DEBUG: Caminho calculado para o banco: {db_path}")

            if not os.path.exists(db_path):
                raise FileNotFoundError(f"Arquivo do banco de dados não encontrado: {db_path}")

            self.conexao = fdb.connect(
                database=db_path,
                user='SYSDBA',
                password='masterkey',
                charset='UTF8'
            )
            print(f"✅ Conectado ao banco: {db_path}")

        except FileNotFoundError as fnf_e:
            print(f"❌ Erro de arquivo ao conectar com banco: {fnf_e}")
            QMessageBox.critical(self, "Erro", f"Erro ao conectar com banco de dados:\n{fnf_e}\nVerifique se o arquivo do banco está no local correto.")
        except Exception as e:
            print(f"❌ Erro ao conectar com banco: {e}")
            QMessageBox.critical(self, "Erro", f"Erro ao conectar com banco de dados:\n{e}")

    def abrir_caixa(self):
        """Abre um novo caixa"""
        if not self.conexao:
            QMessageBox.warning(self, "Erro", "Sem conexão com banco de dados!")
            return
            
        if not self.usuario:
            QMessageBox.warning(self, "Erro", "Usuário não definido!")
            return
        
        # Solicita o fundo de troco
        fundo_troco, ok = QInputDialog.getDouble(
            self, "Abertura de Caixa", 
            "Informe o fundo de troco inicial:", 
            0.00, 0.00, 999999.99, 2
        )
        
        if not ok:
            return
            
        try:
            cursor = self.conexao.cursor()
            
            # Insere novo caixa - o trigger vai gerar o CODIGO automaticamente
            sql = """
                INSERT INTO CAIXA (DATA_ABERTURA, HORA_ABERTURA, USUARIO, FUNDO_TROCO, STATUS)
                VALUES (CURRENT_DATE, CURRENT_TIME, ?, ?, 'ABERTO')
            """
            
            cursor.execute(sql, [self.usuario, fundo_troco])
            self.conexao.commit()
            
            # Para pegar o código gerado, fazemos um SELECT do último registro inserido
            cursor.execute("""
                SELECT CODIGO FROM CAIXA 
                WHERE USUARIO = ? AND DATA_ABERTURA = CURRENT_DATE 
                ORDER BY CODIGO DESC 
                ROWS 1
            """, [self.usuario])
            
            resultado = cursor.fetchone()
            codigo = resultado[0] if resultado else "N/A"
            
            cursor.close()
            
            QMessageBox.information(
                self, "Sucesso", 
                f"Caixa #{codigo} aberto com sucesso!\n"
                f"Fundo de troco: R$ {fundo_troco:.2f}\n"
                f"Usuário: {self.usuario}"
            )
            
            self.carregar_dados()
            
        except Exception as e:
            print(f"❌ Erro ao abrir caixa: {e}")
            QMessageBox.warning(self, "Erro", f"Erro ao abrir caixa:\n{e}")
            if self.conexao:
                self.conexao.rollback()

    def fechar_caixa(self):
        """Fecha o caixa selecionado"""
        if not self.conexao:
            QMessageBox.warning(self, "Erro", "Sem conexão com banco de dados!")
            return
            
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Erro", "Selecione um caixa para fechar!")
            return

        codigo_item = self.table.item(selected, 0)
        data_fechamento_item = self.table.item(selected, 3)
        
        if not codigo_item:
            QMessageBox.warning(self, "Erro", "Código inválido!")
            return
        
        codigo = int(codigo_item.text())
        
        # Verifica se já está fechado
        if data_fechamento_item and data_fechamento_item.text().strip():
            QMessageBox.warning(self, "Aviso", "Este caixa já está fechado!")
            return
        
        # Confirmação com botões "Sim" e "Não"
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle('Confirmação')
        msg_box.setText(f'Deseja realmente fechar o caixa #{codigo}?')
        btn_sim = msg_box.addButton('Sim', QMessageBox.YesRole)
        btn_nao = msg_box.addButton('Não', QMessageBox.NoRole)
        msg_box.setDefaultButton(btn_nao)
        msg_box.exec_()

        if msg_box.clickedButton() == btn_sim:
            try:
                cursor = self.conexao.cursor()
                
                # Atualiza o fechamento
                sql = """
                    UPDATE CAIXA 
                    SET DATA_FECHAMENTO = CURRENT_DATE, 
                        HORA_FECHAMENTO = CURRENT_TIME,
                        STATUS = 'FECHADO'
                    WHERE CODIGO = ?
                """
                
                cursor.execute(sql, [codigo])
                self.conexao.commit()
                cursor.close()
                
                QMessageBox.information(self, "Sucesso", f"Caixa #{codigo} fechado com sucesso!")
                self.carregar_dados()
                
            except Exception as e:
                print(f"❌ Erro ao fechar caixa: {e}")
                QMessageBox.warning(self, "Erro", f"Erro ao fechar caixa:\n{e}")
                if self.conexao:
                    self.conexao.rollback()

    def closeEvent(self, event):
        """Fecha a conexão ao fechar a janela"""
        if self.conexao:
            self.conexao.close()
            print("🔌 Conexão com banco fechada")
        event.accept()


# Teste da janela (descomente para testar isoladamente)
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = ControleCaixaWindow()
    window.set_credentials("ADMIN", "EMPRESA_TESTE", 1)
    window.show()
    sys.exit(app.exec_())