
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo para criação de usuários do sistema com interface gráfica
e gestão de usuários master
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
from tkinter.font import Font
from datetime import datetime, timedelta, date

# Importar funções do módulo banco.py
try:
    import banco
except ImportError:
    # Caso o módulo não esteja no path, tentamos adicionar o diretório pai
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import banco

class CriarUsuarioApp:
    """
    Aplicação para criar usuários no banco de dados
    """
    def __init__(self, root):
        """
        Inicializa a aplicação de criação de usuários
        
        Args:
            root: janela principal do Tkinter
        """
        self.root = root
        self.root.title("Gestão de Usuários")
        self.root.geometry("900x600")  # Tamanho aumentado para acomodar a tabela
        self.root.resizable(True, True)  # Permitir redimensionamento
        
        # Configuração de estilo
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Tema mais moderno
        
        # Configurar cores e fontes
        bg_color = "#f0f0f0"
        self.root.configure(bg=bg_color)
        self.title_font = Font(family="Arial", size=14, weight="bold")
        self.label_font = Font(family="Arial", size=11)
        self.button_font = Font(family="Arial", size=11, weight="bold")
        
        # Título principal
        self.title_label = tk.Label(
            self.root, 
            text="Gestão de Usuários do Sistema", 
            font=self.title_font,
            bg=bg_color,
            pady=10
        )
        self.title_label.pack(fill="x")
        
        # Criando notebook (abas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Aba 1: Criar Usuário
        self.create_tab = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.create_tab, text="Criar Usuário")
        
        # Aba 2: Gerenciar Usuários
        self.manage_tab = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.manage_tab, text="Gerenciar Usuários")
        
        # Aba 3: Gerenciar Licenças
        self.license_tab = tk.Frame(self.notebook, bg=bg_color)
        self.notebook.add(self.license_tab, text="Licenças")
        
        # Inicializar aba de criação
        self.init_create_tab()
        
        # Inicializar aba de gerenciamento
        self.init_manage_tab()
        
        # Inicializar aba de licenças
        self.init_license_tab()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Pronto")
        self.status_bar = tk.Label(
            self.root, 
            textvariable=self.status_var, 
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Centralizar a janela
        self.center_window()
        
        # Verificar conexão com o banco e tabelas
        self.verificar_banco()
        
        # Carregar dados da tabela
        self.carregar_usuarios_master()
    
    def init_create_tab(self):
        """Inicializa a aba de criação de usuário"""
        # Frame principal
        main_frame = tk.Frame(self.create_tab, bg="#f0f0f0", padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Frame para dados do usuário com bordas
        form_frame = tk.LabelFrame(
            main_frame, 
            text="Dados do Usuário", 
            font=self.label_font,
            bg="#f0f0f0", 
            padx=15, 
            pady=15
        )
        form_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Grid de entrada de dados
        row = 0
        
        # Usuário
        tk.Label(
            form_frame, 
            text="Nome de Usuário:", 
            font=self.label_font,
            bg="#f0f0f0", 
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.usuario_var = tk.StringVar()
        self.usuario_entry = tk.Entry(
            form_frame, 
            textvariable=self.usuario_var, 
            font=self.label_font,
            width=30
        )
        self.usuario_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Senha
        tk.Label(
            form_frame, 
            text="Senha:", 
            font=self.label_font,
            bg="#f0f0f0", 
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.senha_var = tk.StringVar()
        self.senha_entry = tk.Entry(
            form_frame, 
            textvariable=self.senha_var, 
            font=self.label_font,
            width=30, 
            show="*"
        )
        self.senha_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Confirmar Senha
        tk.Label(
            form_frame, 
            text="Confirmar Senha:", 
            font=self.label_font,
            bg="#f0f0f0", 
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.conf_senha_var = tk.StringVar()
        self.conf_senha_entry = tk.Entry(
            form_frame, 
            textvariable=self.conf_senha_var, 
            font=self.label_font,
            width=30, 
            show="*"
        )
        self.conf_senha_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Empresa
        tk.Label(
            form_frame, 
            text="Empresa:", 
            font=self.label_font,
            bg="#f0f0f0", 
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.empresa_var = tk.StringVar()
        self.empresa_entry = tk.Entry(
            form_frame, 
            textvariable=self.empresa_var, 
            font=self.label_font,
            width=30
        )
        self.empresa_entry.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Usuário Master (Checkbox)
        self.usuario_master_var = tk.BooleanVar()
        self.usuario_master_check = tk.Checkbutton(
            form_frame,
            text="Usuário Master (Cliente Principal)", 
            variable=self.usuario_master_var,
            font=self.label_font,
            bg="#f0f0f0",
            command=self.toggle_mensalidade_fields
        )
        self.usuario_master_check.grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Frame para Mensalidades (inicialmente escondido)
        self.mensalidade_frame = tk.Frame(form_frame, bg="#f0f0f0")
        self.mensalidade_frame.grid(row=row, column=0, columnspan=2, sticky="ew", pady=5)
        self.mensalidade_frame.grid_remove()  # Esconder inicialmente
        
        mensalidade_row = 0
        
        # Número de mensalidades
        tk.Label(
            self.mensalidade_frame, 
            text="Meses de Acesso:", 
            font=self.label_font,
            bg="#f0f0f0", 
            anchor="w"
        ).grid(row=mensalidade_row, column=0, sticky="w", pady=5)
        
        self.meses_var = tk.StringVar()
        self.meses_var.set("1")  # Valor padrão
        meses_values = [str(i) for i in range(1, 13)]  # 1 a 12 meses
        self.meses_combo = ttk.Combobox(
            self.mensalidade_frame, 
            textvariable=self.meses_var,
            values=meses_values,
            width=5,
            state="readonly"
        )
        self.meses_combo.grid(row=mensalidade_row, column=1, sticky="w", pady=5)
        self.meses_combo.bind("<<ComboboxSelected>>", self.calcular_data_expiracao)
        mensalidade_row += 1
        
        # Data de Expiração
        tk.Label(
            self.mensalidade_frame, 
            text="Data de Expiração:", 
            font=self.label_font,
            bg="#f0f0f0", 
            anchor="w"
        ).grid(row=mensalidade_row, column=0, sticky="w", pady=5)
        
        self.data_expiracao_var = tk.StringVar()
        self.atualizar_data_expiracao()  # Configurar data padrão
        self.data_expiracao_entry = tk.Entry(
            self.mensalidade_frame, 
            textvariable=self.data_expiracao_var, 
            font=self.label_font,
            width=15,
            state="readonly"
        )
        self.data_expiracao_entry.grid(row=mensalidade_row, column=1, sticky="w", pady=5)
        
        # Mostrar Senha
        row += 1  # Próxima linha após mensalidade_frame
        self.mostrar_senha_var = tk.BooleanVar()
        self.mostrar_senha_check = tk.Checkbutton(
            form_frame,
            text="Mostrar senha", 
            variable=self.mostrar_senha_var,
            font=self.label_font,
            bg="#f0f0f0",
            command=self.toggle_senha_visibility
        )
        self.mostrar_senha_check.grid(row=row, column=1, sticky="w", pady=5)
        
        # Botões de ação
        button_frame = tk.Frame(main_frame, bg="#f0f0f0", pady=10)
        button_frame.pack(fill="x")
        
        # Botão Salvar
        self.salvar_button = tk.Button(
            button_frame,
            text="Criar Usuário",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            command=self.criar_usuario
        )
        self.salvar_button.pack(side=tk.LEFT, padx=10)
        
        # Botão Cancelar
        self.cancelar_button = tk.Button(
            button_frame,
            text="Cancelar",
            font=self.button_font,
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5,
            command=self.limpar_campos
        )
        self.cancelar_button.pack(side=tk.LEFT, padx=10)
        
        # Botão Limpar
        self.limpar_button = tk.Button(
            button_frame,
            text="Limpar",
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
            command=self.limpar_campos
        )
        self.limpar_button.pack(side=tk.LEFT, padx=10)
        
        # Focar no primeiro campo
        self.usuario_entry.focus_set()
    
    def init_manage_tab(self):
        """Inicializa a aba de gerenciamento de usuários"""
        # Frame principal
        main_frame = tk.Frame(self.manage_tab, bg="#f0f0f0", padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Frame para controles
        control_frame = tk.Frame(main_frame, bg="#f0f0f0", pady=10)
        control_frame.pack(fill="x")
        
        # Botão para atualizar lista
        self.atualizar_button = tk.Button(
            control_frame,
            text="Atualizar Lista",
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
            command=self.carregar_usuarios_master
        )
        self.atualizar_button.pack(side=tk.LEFT, padx=10)
        
        # Frame para tabela
        table_frame = tk.Frame(main_frame, bg="#f0f0f0")
        table_frame.pack(fill="both", expand=True, pady=10)
        
        # Tabela de usuários master
        columns = ("ID", "Usuário", "Empresa", "Status", "Data Expiração", "Funcionários")
        self.usuarios_table = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Definir cabeçalhos
        for col in columns:
            self.usuarios_table.heading(col, text=col)
            if col == "Usuário" or col == "Empresa":
                self.usuarios_table.column(col, width=150, anchor="w")
            elif col == "ID":
                self.usuarios_table.column(col, width=50, anchor="center")
            else:
                self.usuarios_table.column(col, width=100, anchor="center")
        
        # Scrollbars
        yscrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.usuarios_table.yview)
        self.usuarios_table.configure(yscrollcommand=yscrollbar.set)
        
        xscrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.usuarios_table.xview)
        self.usuarios_table.configure(xscrollcommand=xscrollbar.set)
        
        # Layout
        self.usuarios_table.pack(side="left", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        xscrollbar.pack(side="bottom", fill="x")
        
        # Frame para botões de ação
        action_frame = tk.Frame(main_frame, bg="#f0f0f0", pady=10)
        action_frame.pack(fill="x")
        
        # Botão para bloquear usuário
        self.bloquear_button = tk.Button(
            action_frame,
            text="Bloquear Usuário",
            font=self.button_font,
            bg="#f44336",
            fg="white",
            padx=15,
            pady=5,
            command=self.bloquear_usuario
        )
        self.bloquear_button.pack(side=tk.LEFT, padx=10)
        
        # Botão para liberar usuário
        self.liberar_button = tk.Button(
            action_frame,
            text="Liberar Usuário",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            command=self.liberar_usuario
        )
        self.liberar_button.pack(side=tk.LEFT, padx=10)
        
        # Botão para renovar mensalidade
        self.renovar_button = tk.Button(
            action_frame,
            text="Renovar Mensalidade",
            font=self.button_font,
            bg="#FF9800",
            fg="white",
            padx=15,
            pady=5,
            command=self.renovar_mensalidade
        )
        self.renovar_button.pack(side=tk.LEFT, padx=10)
    
    def init_license_tab(self):
        """Inicializa a aba de gerenciamento de licenças"""
        # Frame principal
        main_frame = tk.Frame(self.license_tab, bg="#f0f0f0", padx=20, pady=10)
        main_frame.pack(fill="both", expand=True)
        
        # Frame para controles
        control_frame = tk.LabelFrame(
            main_frame,
            text="Gerar Código de Licença",
            font=self.label_font,
            bg="#f0f0f0",
            padx=15,
            pady=15
        )
        control_frame.pack(fill="x", padx=10, pady=10)
        
        # Seleção de usuário
        row = 0
        tk.Label(
            control_frame,
            text="Usuário:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.usuario_licenca_var = tk.StringVar()
        self.usuario_licenca_combo = ttk.Combobox(
            control_frame,
            textvariable=self.usuario_licenca_var,
            width=30,
            state="readonly"
        )
        self.usuario_licenca_combo.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Meses de validade
        tk.Label(
            control_frame,
            text="Meses de Validade:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.meses_licenca_var = tk.StringVar()
        self.meses_licenca_var.set("1")
        meses_values = [str(i) for i in range(1, 13)]
        self.meses_licenca_combo = ttk.Combobox(
            control_frame,
            textvariable=self.meses_licenca_var,
            values=meses_values,
            width=5,
            state="readonly"
        )
        self.meses_licenca_combo.grid(row=row, column=1, sticky="w", pady=5)
        row += 1
        
        # Código gerado
        tk.Label(
            control_frame,
            text="Código Gerado:",
            font=self.label_font,
            bg="#f0f0f0",
            anchor="w"
        ).grid(row=row, column=0, sticky="w", pady=5)
        
        self.codigo_licenca_var = tk.StringVar()
        self.codigo_licenca_entry = tk.Entry(
            control_frame,
            textvariable=self.codigo_licenca_var,
            font=self.label_font,
            width=40,
            state="readonly"
        )
        self.codigo_licenca_entry.grid(row=row, column=1, sticky="w", pady=5)
        
        # Botão Copiar
        self.copiar_button = tk.Button(
            control_frame,
            text="Copiar",
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=2,
            command=self.copiar_codigo_licenca
        )
        self.copiar_button.grid(row=row, column=2, padx=5, pady=5)
        row += 1
        
        # Botões de ação
        button_frame = tk.Frame(control_frame, bg="#f0f0f0", pady=10)
        button_frame.grid(row=row, column=0, columnspan=3, sticky="w", pady=5)
        
        # Botão Gerar Código
        self.gerar_codigo_button = tk.Button(
            button_frame,
            text="Gerar Código",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            padx=15,
            pady=5,
            command=self.gerar_codigo_licenca
        )
        self.gerar_codigo_button.pack(side=tk.LEFT, padx=10)
        
        # Frame para histórico de licenças
        history_frame = tk.LabelFrame(
            main_frame,
            text="Histórico de Licenças",
            font=self.label_font,
            bg="#f0f0f0",
            padx=15,
            pady=15
        )
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Tabela de licenças
        columns = ("ID", "Usuário", "Data Geração", "Data Expiração", "Código", "Status")
        self.licencas_table = ttk.Treeview(
            history_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )
        
        # Definir cabeçalhos
        for col in columns:
            self.licencas_table.heading(col, text=col)
            if col == "Código":
                self.licencas_table.column(col, width=200, anchor="w")
            elif col == "ID":
                self.licencas_table.column(col, width=50, anchor="center")
            else:
                self.licencas_table.column(col, width=100, anchor="center")
        
        # Scrollbars
        yscrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.licencas_table.yview)
        self.licencas_table.configure(yscrollcommand=yscrollbar.set)
        
        # Layout
        self.licencas_table.pack(side="left", fill="both", expand=True)
        yscrollbar.pack(side="right", fill="y")
        
        # Carregar usuários na ComboBox
        self.carregar_usuarios_para_licenca()
        
        # Botão para atualizar histórico
        atualizar_historico_button = tk.Button(
            history_frame,
            text="Atualizar Histórico",
            font=self.button_font,
            bg="#2196F3",
            fg="white",
            padx=15,
            pady=5,
            command=self.carregar_historico_licencas
        )
        atualizar_historico_button.pack(side=tk.BOTTOM, padx=10, pady=10)
    
    def carregar_historico_licencas(self):
        """Carrega o histórico de licenças na tabela"""
        # Limpar tabela
        for item in self.licencas_table.get_children():
            self.licencas_table.delete(item)
            
        try:
            # Buscar licenças
            query = """
            SELECT L.ID, U.USUARIO, L.DATA_GERACAO, L.DATA_EXPIRACAO, L.CODIGO, L.ATIVO
            FROM LICENCAS L
            JOIN USUARIOS U ON L.USUARIO_ID = U.ID
            ORDER BY L.DATA_GERACAO DESC
            """
            from banco import execute_query
            licencas = execute_query(query)
            
            if not licencas:
                self.status_var.set("Nenhuma licença encontrada")
                return
                
            # Preencher tabela
            for lic in licencas:
                lic_id, username, data_geracao, data_expiracao, codigo, ativo = lic
                
                # Formatar datas
                data_geracao_str = ""
                if data_geracao:
                    try:
                        if isinstance(data_geracao, str):
                            data_geracao_str = data_geracao
                        else:
                            data_geracao_str = data_geracao.strftime("%d/%m/%Y")
                    except:
                        data_geracao_str = str(data_geracao)
                
                data_expiracao_str = ""
                if data_expiracao:
                    try:
                        if isinstance(data_expiracao, str):
                            data_expiracao_str = data_expiracao
                        else:
                            data_expiracao_str = data_expiracao.strftime("%d/%m/%Y")
                    except:
                        data_expiracao_str = str(data_expiracao)
                
                # Status
                status = "Ativo" if ativo and ativo.upper() == 'S' else "Inativo"
                
                # Inserir na tabela
                self.licencas_table.insert("", "end", values=(
                    lic_id, username, data_geracao_str, data_expiracao_str, codigo, status))
                
            self.status_var.set(f"{len(licencas)} licenças encontradas")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar licenças: {str(e)}")
            self.status_var.set(f"Erro: {str(e)}")
    
    def carregar_usuarios_para_licenca(self):
        """Carrega os usuários para o ComboBox de licenças"""
        try:
            # Buscar usuários master
            query = """
            SELECT ID, USUARIO, EMPRESA
            FROM USUARIOS
            WHERE USUARIO_MASTER IS NULL
            ORDER BY EMPRESA, USUARIO
            """
            from banco import execute_query
            usuarios = execute_query(query)
            
            # Preencher o ComboBox
            opcoes = []
            self.usuarios_licenca_map = {}  # Mapear texto -> ID
            
            for user in usuarios:
                user_id, username, empresa = user
                texto = f"{username} ({empresa})"
                opcoes.append(texto)
                self.usuarios_licenca_map[texto] = user_id
            
            self.usuario_licenca_combo['values'] = opcoes
            if opcoes:
                self.usuario_licenca_combo.current(0)
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar usuários: {str(e)}")
    
    def gerar_codigo_licenca(self):
        """Gera um código de licença para o usuário selecionado"""
        try:
            # Verificar seleção
            usuario_texto = self.usuario_licenca_var.get()
            if not usuario_texto:
                messagebox.showwarning("Seleção necessária", "Selecione um usuário para gerar o código.")
                return
            
            # Obter dados
            usuario_id = self.usuarios_licenca_map[usuario_texto]
            meses = int(self.meses_licenca_var.get())
            data_atual = date.today()
            data_expiracao = data_atual + timedelta(days=meses * 30)
            
            # Gerar código
            from banco import gerar_codigo_licenca, salvar_codigo_licenca
            codigo = gerar_codigo_licenca(usuario_id, data_expiracao)
            
            # Salvar no banco
            salvar_codigo_licenca(usuario_id, codigo, data_atual, data_expiracao)
            
            # Exibir o código
            self.codigo_licenca_var.set(codigo)
            
            # Atualizar o histórico de licenças
            self.carregar_historico_licencas()
            
            messagebox.showinfo("Sucesso", f"Código de licença gerado com sucesso!\nValidade: {data_expiracao.strftime('%d/%m/%Y')}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao gerar código: {str(e)}")
    
    def copiar_codigo_licenca(self):
        """Copia o código para a área de transferência"""
        codigo = self.codigo_licenca_var.get()
        if not codigo:
            messagebox.showwarning("Código vazio", "Primeiro gere um código de licença.")
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(codigo)
        self.root.update()
        
        messagebox.showinfo("Copiado", "Código copiado para a área de transferência.")
    
    def renovar_mensalidade(self):
        """Renova a mensalidade do usuário selecionado"""
        selected_item = self.usuarios_table.selection()
        if not selected_item:
            messagebox.showwarning("Seleção necessária", "Selecione um usuário para renovar a mensalidade.")
            return
            
        # Obter ID do usuário selecionado
        user_id = self.usuarios_table.item(selected_item[0])["values"][0]
        
        # Criar diálogo para quantidade de meses
        dialog = tk.Toplevel(self.root)
        dialog.title("Renovar Mensalidade")
        dialog.geometry("300x150")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Centralizar o diálogo
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # Layout do diálogo
        frame = tk.Frame(dialog, padx=20, pady=20)
        frame.pack(fill="both", expand=True)
        
        # Número de meses
        tk.Label(
            frame, 
            text="Meses de Acesso:", 
            font=self.label_font
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        meses_var = tk.StringVar()
        meses_var.set("1")  # Valor padrão
        meses_values = [str(i) for i in range(1, 13)]  # 1 a 12 meses
        meses_combo = ttk.Combobox(
            frame, 
            textvariable=meses_var,
            values=meses_values,
            width=5,
            state="readonly"
        )
        meses_combo.grid(row=0, column=1, sticky="w", pady=5)
        
        # Botões do diálogo
        button_frame = tk.Frame(frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        # Função para confirmar
        def confirmar():
            meses = int(meses_var.get())
            # Calcular nova data de expiração
            nova_data = date.today() + timedelta(days=meses * 30)
            
            try:
                # Importar função para atualizar data
                from banco import atualizar_data_expiracao
                atualizar_data_expiracao(user_id, nova_data)
                
                # Desbloquear usuário se estava bloqueado
                from banco import desbloquear_usuario
                desbloquear_usuario(user_id)
                
                messagebox.showinfo("Sucesso", f"Mensalidade renovada por {meses} meses.\nNova data de expiração: {nova_data.strftime('%d/%m/%Y')}")
                
                # Recarregar tabela
                self.carregar_usuarios_master()
                
                dialog.destroy()
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao renovar mensalidade: {str(e)}")
                dialog.destroy()
        
        tk.Button(
            button_frame,
            text="Confirmar",
            font=self.button_font,
            bg="#4CAF50",
            fg="white",
            padx=10,
            pady=2,
            command=confirmar
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancelar",
            font=self.button_font,
            bg="#f44336",
            fg="white",
            padx=10,
            pady=2,
            command=dialog.destroy
        ).pack(side=tk.LEFT, padx=5)
    
    def bloquear_usuario(self):
        """Bloqueia o usuário selecionado"""
        selected_item = self.usuarios_table.selection()
        if not selected_item:
            messagebox.showwarning("Seleção necessária", "Selecione um usuário para bloquear.")
            return
            
        # Obter ID do usuário selecionado
        user_id = self.usuarios_table.item(selected_item[0])["values"][0]
        username = self.usuarios_table.item(selected_item[0])["values"][1]
        
        # Confirmar bloqueio
        if not messagebox.askyesno("Confirmar bloqueio", f"Deseja realmente bloquear o usuário {username}?\n\nTodos os usuários vinculados também serão bloqueados."):
            return
            
        # Solicitar motivo do bloqueio
        motivo = simpledialog.askstring("Motivo do bloqueio", "Digite o motivo do bloqueio:")
        
        try:
            # Importar função para bloquear usuário
            from banco import bloquear_usuario
            bloquear_usuario(user_id, motivo)
            
            messagebox.showinfo("Sucesso", f"Usuário {username} bloqueado com sucesso!")
            
            # Recarregar tabela
            self.carregar_usuarios_master()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao bloquear usuário: {str(e)}")
    
    def liberar_usuario(self):
        """Libera o usuário selecionado"""
        selected_item = self.usuarios_table.selection()
        if not selected_item:
            messagebox.showwarning("Seleção necessária", "Selecione um usuário para liberar.")
            return
            
        # Obter ID do usuário selecionado
        user_id = self.usuarios_table.item(selected_item[0])["values"][0]
        username = self.usuarios_table.item(selected_item[0])["values"][1]
        
        # Confirmar liberação
        if not messagebox.askyesno("Confirmar liberação", f"Deseja realmente liberar o usuário {username}?"):
            return
            
        try:
            # Importar função para desbloquear usuário
            from banco import desbloquear_usuario
            desbloquear_usuario(user_id)
            
            messagebox.showinfo("Sucesso", f"Usuário {username} liberado com sucesso!")
            
            # Recarregar tabela
            self.carregar_usuarios_master()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao liberar usuário: {str(e)}")
    
    def carregar_usuarios_master(self):
        """Carrega os usuários master na tabela"""
        # Limpar tabela
        for item in self.usuarios_table.get_children():
            self.usuarios_table.delete(item)
            
        try:
            # Buscar usuários master
            query = """
            SELECT 
                U.ID, 
                U.USUARIO, 
                U.EMPRESA, 
                U.BLOQUEADO, 
                U.DATA_EXPIRACAO,
                (SELECT COUNT(*) FROM USUARIOS WHERE USUARIO_MASTER = U.ID) AS QTD_FUNCIONARIOS
            FROM USUARIOS U
            WHERE U.USUARIO_MASTER IS NULL
            ORDER BY U.EMPRESA, U.USUARIO
            """
            from banco import execute_query
            usuarios = execute_query(query)
            
            if not usuarios:
                self.status_var.set("Nenhum usuário master encontrado")
                return
                
            # Preencher tabela
            for user in usuarios:
                user_id, username, empresa, bloqueado, data_expiracao, qtd_func = user
                
                # Formatação do status
                status = "Bloqueado" if bloqueado and bloqueado.upper() == 'S' else "Ativo"
                
                # Formatação da data
                data_str = ""
                if data_expiracao:
                    try:
                        if isinstance(data_expiracao, str):
                            data_str = data_expiracao
                        else:
                            data_str = data_expiracao.strftime("%d/%m/%Y")
                            
                        # Verificar se está vencido
                        if date.today() > data_expiracao:
                            status = "Vencido"
                    except:
                        data_str = str(data_expiracao)
                
                # Inserir na tabela
                self.usuarios_table.insert("", "end", values=(user_id, username, empresa, status, data_str, qtd_func))
                
            self.status_var.set(f"{len(usuarios)} usuários master encontrados")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar usuários: {str(e)}")
            self.status_var.set(f"Erro: {str(e)}")
    
    def verificar_banco(self):
        """
        Verifica a conexão com o banco de dados e a existência das tabelas necessárias
        """
        try:
            # Verificar se a tabela de usuários existe
            banco.verificar_tabela_usuarios()
            
            # Verificar se a tabela de licenças existe
            banco.verificar_tabela_licencas()
            
            # Verificar se a tabela tem os campos necessários
            self.verificar_campos_adicionais()
            
            # Verificar quantos usuários já existem
            usuarios = banco.listar_usuarios()
            if usuarios:
                msg = f"Existem {len(usuarios)} usuários cadastrados."
                self.status_var.set(msg)
            else:
                self.status_var.set("Nenhum usuário cadastrado. Crie o primeiro usuário.")
                
        except Exception as e:
            messagebox.showerror("Erro de Conexão", 
                                 f"Não foi possível conectar ao banco de dados: {str(e)}")
            self.status_var.set("Erro de conexão com o banco")
    
    def verificar_campos_adicionais(self):
        """Verifica se os campos adicionais existem na tabela de usuários"""
        try:
            # Verificar se os campos necessários existem
            query = """
            SELECT COUNT(*) FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'USUARIOS' 
            AND RDB$FIELD_NAME = 'BLOQUEADO'
            """
            from banco import execute_query
            result = execute_query(query)
            
            # Se o campo não existe, adicionar os campos necessários
            if result[0][0] == 0:
                self.status_var.set("Adicionando campos necessários à tabela de usuários...")
                
                # Adicionar campos
                queries = [
                    "ALTER TABLE USUARIOS ADD BLOQUEADO CHAR(1) DEFAULT 'N'",
                    "ALTER TABLE USUARIOS ADD DATA_BLOQUEIO DATE",
                    "ALTER TABLE USUARIOS ADD MOTIVO_BLOQUEIO VARCHAR(100)",
                    "ALTER TABLE USUARIOS ADD USUARIO_MASTER INTEGER",
                    "ALTER TABLE USUARIOS ADD DATA_EXPIRACAO DATE"
                ]
                
                for query in queries:
                    execute_query(query)
                
                self.status_var.set("Campos adicionados com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", 
                              f"Falha ao verificar campos da tabela: {str(e)}")
            self.status_var.set(f"Erro: {str(e)}")
    
    def toggle_senha_visibility(self):
        """
        Alterna a visibilidade da senha
        """
        if self.mostrar_senha_var.get():
            self.senha_entry.config(show="")
            self.conf_senha_entry.config(show="")
        else:
            self.senha_entry.config(show="*")
            self.conf_senha_entry.config(show="*")
    
    def toggle_mensalidade_fields(self):
        """Mostra ou esconde os campos de mensalidade"""
        if self.usuario_master_var.get():
            self.mensalidade_frame.grid()
            self.atualizar_data_expiracao()
        else:
            self.mensalidade_frame.grid_remove()
    
    def atualizar_data_expiracao(self):
        """Atualiza a data de expiração padrão (hoje + X meses)"""
        try:
            meses = int(self.meses_var.get())
            data_atual = date.today()
            data_expiracao = data_atual + timedelta(days=meses * 30)  # Aproximação de mês
            self.data_expiracao_var.set(data_expiracao.strftime("%d/%m/%Y"))
        except:
            self.data_expiracao_var.set("")
    
    def calcular_data_expiracao(self, event=None):
        """Calcula a data de expiração com base nos meses selecionados"""
        self.atualizar_data_expiracao()
    
    def limpar_campos(self):
        """
        Limpa todos os campos do formulário
        """
        self.usuario_var.set("")
        self.senha_var.set("")
        self.conf_senha_var.set("")
        self.empresa_var.set("")
        self.usuario_master_var.set(False)
        self.mensalidade_frame.grid_remove()
        self.meses_var.set("1")
        self.atualizar_data_expiracao()
        self.usuario_entry.focus_set()
    
    def criar_usuario(self):
        """
        Valida os dados e cria o usuário no banco
        """
        # Obter dados do formulário
        usuario = self.usuario_var.get().strip()
        senha = self.senha_var.get().strip()
        conf_senha = self.conf_senha_var.get().strip()
        empresa = self.empresa_var.get().strip()
        
        # Verificar se é usuário master
        is_master = self.usuario_master_var.get()
        
        # Validar campos
        if not usuario:
            messagebox.showerror("Erro", "O nome de usuário é obrigatório")
            self.usuario_entry.focus_set()
            return
        
        if not senha:
            messagebox.showerror("Erro", "A senha é obrigatória")
            self.senha_entry.focus_set()
            return
        
        if senha != conf_senha:
            messagebox.showerror("Erro", "As senhas não conferem")
            self.conf_senha_entry.focus_set()
            return
        
        if not empresa:
            messagebox.showerror("Erro", "O nome da empresa é obrigatório")
            self.empresa_entry.focus_set()
            return
        
        # Configurar data de expiração para usuários master
        data_expiracao = None
        if is_master:
            try:
                data_str = self.data_expiracao_var.get()
                data_parts = data_str.split('/')
                data_expiracao = date(int(data_parts[2]), int(data_parts[1]), int(data_parts[0]))
            except:
                messagebox.showerror("Erro", "Data de expiração inválida")
                return
        
        # Criar usuário no banco
        try:
            self.status_var.set("Criando usuário...")
            self.root.update_idletasks()
            
            # Chamar função do banco para criar usuário
            resultado = banco.criar_usuario(
                usuario, 
                senha, 
                empresa, 
                usuario_master=None,  # Sempre None pois este é um usuário master ou normal
                data_expiracao=data_expiracao if is_master else None
            )
            
            if resultado:
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                self.status_var.set("Usuário criado com sucesso")
                
                # Atualizar tabela se for usuário master
                if is_master:
                    self.notebook.select(1)  # Mudar para a aba de gerenciamento
                    self.carregar_usuarios_master()
                
                # Limpar campos
                self.limpar_campos()
            else:
                messagebox.showerror("Erro", "Não foi possível criar o usuário")
                self.status_var.set("Erro ao criar usuário")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar usuário: {str(e)}")
            self.status_var.set(f"Erro: {str(e)}")
    
    def center_window(self):
        """
        Centraliza a janela na tela
        """
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def main():
    """
    Função principal que inicia a aplicação
    """
    root = tk.Tk()
    app = CriarUsuarioApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()