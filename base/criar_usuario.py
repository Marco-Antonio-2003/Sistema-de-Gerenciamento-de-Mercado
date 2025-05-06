#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Módulo para criação de usuários do sistema com interface gráfica
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter.font import Font

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
        self.root.title("Criação de Usuário")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
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
            text="Criação de Usuário do Sistema", 
            font=self.title_font,
            bg=bg_color,
            pady=10
        )
        self.title_label.pack(fill="x")
        
        # Frame principal
        self.main_frame = tk.Frame(self.root, bg=bg_color, padx=20, pady=10)
        self.main_frame.pack(fill="both", expand=True)
        
        # Dados do usuário
        self.create_form()
        
        # Botões de ação
        self.create_buttons()
        
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
    
    def verificar_banco(self):
        """
        Verifica a conexão com o banco de dados e a existência das tabelas necessárias
        """
        try:
            # Verificar se a tabela de usuários existe
            banco.verificar_tabela_usuarios()
            
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
    
    def create_form(self):
        """
        Cria o formulário para entrada de dados do usuário
        """
        # Frame para dados do usuário com bordas
        form_frame = tk.LabelFrame(
            self.main_frame, 
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
        
        # Mostrar Senha
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
        
        # Focar no primeiro campo
        self.usuario_entry.focus_set()
    
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
    
    def create_buttons(self):
        """
        Cria os botões de ação
        """
        # Frame para botões
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0", pady=10)
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
            command=self.root.destroy
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
    
    def limpar_campos(self):
        """
        Limpa todos os campos do formulário
        """
        self.usuario_var.set("")
        self.senha_var.set("")
        self.conf_senha_var.set("")
        self.empresa_var.set("")
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
        
        # Criar usuário no banco
        try:
            self.status_var.set("Criando usuário...")
            self.root.update_idletasks()
            
            # Chamar função do banco para criar usuário
            resultado = banco.criar_usuario(usuario, senha, empresa)
            
            if resultado:
                messagebox.showinfo("Sucesso", "Usuário criado com sucesso!")
                self.status_var.set("Usuário criado com sucesso")
                
                # Limpar campos
                self.limpar_campos()
                
                # Perguntar se deseja criar outro usuário ou sair
                if not messagebox.askyesno("Continuar", "Deseja criar outro usuário?"):
                    self.root.destroy()
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