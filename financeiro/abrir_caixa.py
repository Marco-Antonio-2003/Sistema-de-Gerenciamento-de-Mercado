#abrir caixa
import sys
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QFormLayout, 
                            QDateEdit, QTimeEdit, QComboBox, QSpinBox, 
                            QDoubleSpinBox, QMessageBox)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QDate, QTime

class AbrirCaixa(QDialog):
    def __init__(self, codigo=None, tipo_operacao=None, parent=None):
        super().__init__(parent)
        self.codigo = codigo
        self.tipo_operacao = tipo_operacao
        self.initUI()
        
    def initUI(self):
        # Configuração da janela
        self.setWindowTitle(f"Operação de {self.tipo_operacao} - Caixa {self.codigo}")
        self.setMinimumWidth(500)
        self.setStyleSheet("background-color: #003353; color: white;")
        
        # Layout principal
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        titulo = QLabel(f"Operação de {self.tipo_operacao}")
        titulo.setFont(QFont("Arial", 18, QFont.Bold))
        titulo.setStyleSheet("color: white; margin-bottom: 10px;")
        titulo.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(titulo)
        
        # Informações do caixa
        info_layout = QHBoxLayout()
        
        codigo_label = QLabel(f"Código do Caixa: {self.codigo}")
        codigo_label.setFont(QFont("Arial", 12))
        codigo_label.setStyleSheet("color: white;")
        info_layout.addWidget(codigo_label)
        
        info_layout.addStretch(1)
        
        main_layout.addLayout(info_layout)
        
        # Linha separadora
        separator = QLabel()
        separator.setStyleSheet("background-color: #004465; min-height: 2px; margin: 10px 0px;")
        main_layout.addWidget(separator)
        
        # Formulário
        form_layout = QFormLayout()
        form_layout.setVerticalSpacing(15)
        form_layout.setHorizontalSpacing(20)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        
        # Estilo para labels
        label_style = "color: white; font-size: 14px;"
        
        # Estilo para inputs
        input_style = """
            background-color: #fffff0;
            border: 1px solid #cccccc;
            border-radius: 5px;
            padding: 8px;
            font-size: 14px;
            min-height: 25px;
            color: black;
        """
        combo_style = input_style + """
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(dropdown.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
            }
        """
        
        # Data e Hora
        data_label = QLabel("Data:")
        data_label.setStyleSheet(label_style)
        self.data_edit = QDateEdit(QDate.currentDate())
        self.data_edit.setCalendarPopup(True)
        self.data_edit.setStyleSheet(input_style)
        form_layout.addRow(data_label, self.data_edit)
        
        hora_label = QLabel("Hora:")
        hora_label.setStyleSheet(label_style)
        self.hora_edit = QTimeEdit(QTime.currentTime())
        self.hora_edit.setStyleSheet(input_style)
        form_layout.addRow(hora_label, self.hora_edit)
        
        # Campos específicos para Entrada ou Saída
        if self.tipo_operacao == "Entrada":
            # Campos específicos para entrada
            valor_label = QLabel("Valor de Entrada:")
            valor_label.setStyleSheet(label_style)
            self.valor_spin = QDoubleSpinBox()
            self.valor_spin.setRange(0.00, 9999999.99)
            self.valor_spin.setDecimals(2)
            self.valor_spin.setSingleStep(10.00)
            self.valor_spin.setPrefix("R$ ")
            self.valor_spin.setValue(0.00)
            self.valor_spin.setStyleSheet(input_style)
            form_layout.addRow(valor_label, self.valor_spin)
            
            motivo_label = QLabel("Motivo da Entrada:")
            motivo_label.setStyleSheet(label_style)
            self.motivo_combo = QComboBox()
            self.motivo_combo.addItems(["Abertura de Caixa", "Reforço", "Correção", "Outros"])
            self.motivo_combo.setStyleSheet(combo_style)
            form_layout.addRow(motivo_label, self.motivo_combo)
            
        else:  # Saída
            # Campos específicos para saída
            valor_label = QLabel("Valor de Saída:")
            valor_label.setStyleSheet(label_style)
            self.valor_spin = QDoubleSpinBox()
            self.valor_spin.setRange(0.00, 9999999.99)
            self.valor_spin.setDecimals(2)
            self.valor_spin.setSingleStep(10.00)
            self.valor_spin.setPrefix("R$ ")
            self.valor_spin.setValue(0.00)
            self.valor_spin.setStyleSheet(input_style)
            form_layout.addRow(valor_label, self.valor_spin)
            
            motivo_label = QLabel("Motivo da Saída:")
            motivo_label.setStyleSheet(label_style)
            self.motivo_combo = QComboBox()
            self.motivo_combo.addItems(["Sangria", "Fechamento", "Devolução", "Cancelamento", "Outros"])
            self.motivo_combo.setStyleSheet(combo_style)
            form_layout.addRow(motivo_label, self.motivo_combo)
        
        # Campo de observação (comum para ambos)
        obs_label = QLabel("Observação:")
        obs_label.setStyleSheet(label_style)
        self.obs_edit = QLineEdit()
        self.obs_edit.setStyleSheet(input_style)
        self.obs_edit.setPlaceholderText("Digite uma observação (opcional)")
        form_layout.addRow(obs_label, self.obs_edit)
        
        # Adicionar o formulário ao layout principal
        main_layout.addLayout(form_layout)
        
        # Botões
        btns_layout = QHBoxLayout()
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setStyleSheet("""
            QPushButton {
                background-color: #fffff0;
                color: black;
                padding: 8px 15px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #e6e6e6;
            }
            QPushButton:pressed {
                background-color: #cccccc;
            }
        """)
        self.btn_cancelar.clicked.connect(self.reject)
        
        self.btn_confirmar = QPushButton("Confirmar")
        self.btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #004465;
                color: white;
                padding: 8px 15px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #00354f;
            }
            QPushButton:pressed {
                background-color: #0078d7;
            }
        """)
        self.btn_confirmar.clicked.connect(self.confirmar_operacao)
        
        btns_layout.addStretch(1)
        btns_layout.addWidget(self.btn_cancelar)
        btns_layout.addWidget(self.btn_confirmar)
        
        main_layout.addLayout(btns_layout)
    
    def confirmar_operacao(self):
        """Confirma a operação e salva os dados"""
        # Validação básica
        if self.valor_spin.value() <= 0:
            # Cria uma mensagem de aviso
            msg_box = QMessageBox(
                QMessageBox.Warning,
                "Atenção",
                "O valor deve ser maior que zero!",
                QMessageBox.Ok,
                self
            )
            
            # Aplicar estilo com texto branco
            msg_box.setStyleSheet("""
                QMessageBox QLabel {
                    color: white;
                    font-weight: bold;
                }
            """)
            
            # Obter o botão OK e aplicar estilo diretamente nele
            ok_button = msg_box.button(QMessageBox.Ok)
            if ok_button:
                ok_button.setStyleSheet("""
                    QPushButton {
                        color: white;
                        background-color: #004465;
                        border: none;
                        border-radius: 3px;
                        min-width: 80px;
                        min-height: 25px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #00354f;
                    }
                    QPushButton:pressed {
                        background-color: #0078d7;
                    }
                """)
            
            msg_box.exec_()
            return
        
        # Obter os dados do formulário
        data = self.data_edit.date().toString("dd/MM/yyyy")
        hora = self.hora_edit.time().toString("hh:mm")
        valor = self.valor_spin.value()
        motivo = self.motivo_combo.currentText()
        observacao = self.obs_edit.text()
        
        # Aqui você implementaria o código para salvar os dados
        # Por exemplo, salvar em um banco de dados
        
        # Exibir mensagem de sucesso
        msg_box = QMessageBox(
            QMessageBox.Information,
            "Sucesso",
            f"Operação de {self.tipo_operacao} registrada com sucesso!\n"
            f"Data: {data} {hora}\n"
            f"Valor: R$ {valor:.2f}\n"
            f"Motivo: {motivo}",
            QMessageBox.Ok,
            self
        )
        
        # Aplicar estilo com texto branco
        msg_box.setStyleSheet("""
            QMessageBox QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        
        # Obter o botão OK e aplicar estilo diretamente nele
        ok_button = msg_box.button(QMessageBox.Ok)
        if ok_button:
            ok_button.setStyleSheet("""
                QPushButton {
                    color: white;
                    background-color: #004465;
                    border: none;
                    border-radius: 3px;
                    min-width: 80px;
                    min-height: 25px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00354f;
                }
                QPushButton:pressed {
                    background-color: #0078d7;
                }
            """)
        
        msg_box.exec_()
        
        # Fechar o diálogo retornando Accepted
        self.accept()