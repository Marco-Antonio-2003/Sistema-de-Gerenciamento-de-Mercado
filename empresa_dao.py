import sqlite3

class EmpresaDAO:
    """
    Classe de Acesso a Dados (DAO) para a entidade Empresa.
    Implementa as operações CRUD (Create, Read, Update, Delete) para empresas.
    """
    
    def __init__(self, db_path='mb_sistema.db'):
        """
        Inicializa o DAO com o caminho para o banco de dados SQLite.
        
        Args:
            db_path (str): Caminho para o arquivo do banco de dados. Padrão: 'mb_sistema.db'
        """
        self.db_path = db_path
        self.criar_tabela()
    
    def criar_tabela(self):
        """Cria a tabela empresas se não existir."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS empresas (
                    codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT NOT NULL,
                    cnpj TEXT NOT NULL UNIQUE
                )
            ''')
            conn.commit()
    
    def inserir(self, nome, cnpj):
        """
        Insere uma nova empresa no banco de dados.
        
        Args:
            nome (str): Nome da empresa
            cnpj (str): CNPJ da empresa (deve ser único)
            
        Returns:
            int ou None: Código da empresa inserida ou None se ocorrer um erro (ex: CNPJ duplicado)
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO empresas (nome, cnpj) VALUES (?, ?)',
                    (nome, cnpj)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError:
            # CNPJ já existe
            return None
    
    def atualizar(self, codigo, nome, cnpj):
        """
        Atualiza uma empresa existente.
        
        Args:
            codigo (int): Código da empresa a ser atualizada
            nome (str): Novo nome da empresa
            cnpj (str): Novo CNPJ da empresa
            
        Returns:
            bool: True se a atualização foi bem-sucedida, False caso contrário
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE empresas SET nome = ?, cnpj = ? WHERE codigo = ?',
                    (nome, cnpj, codigo)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            # CNPJ já existe em outra empresa
            return False
    
    def excluir(self, codigo):
        """
        Exclui uma empresa pelo código.
        
        Args:
            codigo (int): Código da empresa a ser excluída
            
        Returns:
            bool: True se a exclusão foi bem-sucedida, False caso contrário
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM empresas WHERE codigo = ?', (codigo,))
            conn.commit()
            return cursor.rowcount > 0
    
    def listar_todos(self):
        """
        Lista todas as empresas cadastradas.
        
        Returns:
            list: Lista de tuplas (codigo, nome, cnpj)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT codigo, nome, cnpj FROM empresas ORDER BY codigo')
            return cursor.fetchall()
    
    def buscar_por_codigo(self, codigo):
        """
        Busca uma empresa pelo código.
        
        Args:
            codigo (int): Código da empresa
            
        Returns:
            tuple ou None: Tupla (codigo, nome, cnpj) ou None se não encontrada
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT codigo, nome, cnpj FROM empresas WHERE codigo = ?', (codigo,))
            return cursor.fetchone()
    
    def buscar_por_cnpj(self, cnpj):
        """
        Busca uma empresa pelo CNPJ.
        
        Args:
            cnpj (str): CNPJ da empresa
            
        Returns:
            tuple ou None: Tupla (codigo, nome, cnpj) ou None se não encontrada
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT codigo, nome, cnpj FROM empresas WHERE cnpj = ?', (cnpj,))
            return cursor.fetchone()
    
    def buscar_por_nome(self, nome):
        """
        Busca empresas pelo nome (busca parcial, case insensitive).
        
        Args:
            nome (str): Parte do nome a ser buscado
            
        Returns:
            list: Lista de tuplas (codigo, nome, cnpj)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT codigo, nome, cnpj FROM empresas WHERE nome LIKE ? ORDER BY nome', ('%' + nome + '%',))
            return cursor.fetchall()