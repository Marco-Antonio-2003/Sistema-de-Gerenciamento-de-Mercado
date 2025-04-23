"""
Módulo para gerenciar conexões com o banco de dados Firebird
"""

#banco.py
import os
import sys
import fdb  # Módulo para conexão com Firebird
from PyQt5.QtWidgets import QMessageBox

# Função para encontrar o caminho do banco de dados
def get_db_path():
    """
    Determina o caminho do banco de dados considerando diferentes ambientes
    de execução (desenvolvimento ou aplicação compilada)
    """
    # Opção 1: Verifica se estamos em uma aplicação compilada (PyInstaller)
    if getattr(sys, 'frozen', False):
        # Se estiver executando como um executável compilado
        base_dir = os.path.dirname(sys.executable)
        db_paths = [
            # Caminho relativo ao executável
            os.path.join(base_dir, "base", "MBDATA_NOVO.FDB"),
            # Caminho relativo ao executável (pasta pai)
            os.path.join(os.path.dirname(base_dir), "base", "MBDATA_NOVO.FDB"),
            # Caminho absoluto fixo (caso seja uma instalação específica)
            r"C:\MBSistema\base\MBDATA_NOVO.FDB",
        ]
    else:
        # Se estiver executando em modo de desenvolvimento
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_paths = [
            # Caminho relativo ao script atual
            os.path.join(base_dir, "base", "MBDATA_NOVO.FDB"),
            # Caminho alternativo (um nível acima)
            os.path.join(os.path.dirname(base_dir), "base", "MBDATA_NOVO.FDB"),
        ]
    
    # Verificar qual caminho existe
    for path in db_paths:
        if os.path.isfile(path):
            print(f"Banco de dados encontrado em: {path}")
            return path
    
    # Se chegou até aqui, não encontrou o arquivo
    # Vamos retornar o primeiro caminho e deixar o Firebird gerar o erro apropriado
    print(f"AVISO: Banco de dados não encontrado. Tentando usar: {db_paths[0]}")
    
    # Verificar se o diretório existe, se não, tentar criá-lo
    db_dir = os.path.dirname(db_paths[0])
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"Diretório criado: {db_dir}")
        except Exception as e:
            print(f"Erro ao criar diretório: {e}")
    
    return db_paths[0]

# Configurações do banco de dados
DB_PATH = get_db_path()
DB_USER = "SYSDBA"
DB_PASSWORD = "masterkey"
DB_HOST = "localhost"
DB_PORT = 3050

def get_connection():
    """
    Retorna uma conexão com o banco de dados Firebird
    """
    try:
        print(f"Tentando conectar ao banco de dados: {DB_PATH}")
        conn = fdb.connect(
            host=DB_HOST,
            database=DB_PATH,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            charset='UTF8'  # Garantir codificação correta
        )
        return conn
    except Exception as e:
        print(f"Erro de conexão: {e}")
        raise Exception(f"Erro ao conectar ao banco de dados: {str(e)}")

def execute_query(query, params=None, commit=True):
    """
    Executa uma query no banco de dados
    
    Args:
        query (str): Query SQL a ser executada
        params (tuple, optional): Parâmetros para a query
        commit (bool, optional): Se deve fazer commit após a execução
        
    Returns:
        list: Resultados da query (se for SELECT)
    """
    conn = None
    cursor = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        if params:
            print(f"Executando query com parâmetros: {params}")
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        # Se for um SELECT, retorna os resultados
        if query.strip().upper().startswith("SELECT"):
            results = cursor.fetchall()
            return results
        
        # Se precisar fazer commit
        if commit:
            conn.commit()
            
        return True
    except Exception as e:
        if conn and commit:
            conn.rollback()
        print(f"Erro na execução da query: {str(e)}")
        raise Exception(f"Erro ao executar query: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def validar_login(usuario, senha, empresa):
    """
    Valida o login do usuário
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha do usuário
        empresa (str): Nome da empresa
        
    Returns:
        bool: True se o login for válido, False caso contrário
    """
    try:
        query = """
        SELECT COUNT(*) FROM USUARIOS 
        WHERE USUARIO = ? AND SENHA = ? AND EMPRESA = ?
        """
        result = execute_query(query, (usuario, senha, empresa))
        
        # Se encontrou pelo menos um usuário com essas credenciais
        return result[0][0] > 0
    except Exception as e:
        print(f"Erro na validação de login: {e}")
        raise Exception(f"Erro ao validar login: {str(e)}")

def criar_usuario(usuario, senha, empresa):
    """
    Cria um novo usuário no banco de dados
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha do usuário
        empresa (str): Nome da empresa
    
    Returns:
        bool: True se o usuário foi criado com sucesso
    """
    try:
        # Verificar se o usuário já existe
        query_check = """
        SELECT COUNT(*) FROM USUARIOS 
        WHERE USUARIO = ? AND EMPRESA = ?
        """
        result = execute_query(query_check, (usuario, empresa))
        
        if result[0][0] > 0:
            raise Exception("Usuário já existe para esta empresa")
        
        # Obter o próximo ID
        query_nextid = """
        SELECT COALESCE(MAX(ID), 0) + 1 FROM USUARIOS
        """
        next_id = execute_query(query_nextid)[0][0]
        
        # Inserir novo usuário com ID explícito
        query_insert = """
        INSERT INTO USUARIOS (ID, USUARIO, SENHA, EMPRESA) 
        VALUES (?, ?, ?, ?)
        """
        execute_query(query_insert, (next_id, usuario, senha, empresa))
        
        return True
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        raise Exception(f"Erro ao criar usuário: {str(e)}")

def verificar_tabela_usuarios():
    """
    Verifica se a tabela USUARIOS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'USUARIOS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela USUARIOS não encontrada. Criando...")
            query_create = """
            CREATE TABLE USUARIOS (
                ID INTEGER NOT NULL PRIMARY KEY,
                USUARIO VARCHAR(50) NOT NULL,
                SENHA VARCHAR(200) NOT NULL,
                EMPRESA VARCHAR(50) NOT NULL
            )
            """
            execute_query(query_create)
            print("Tabela USUARIOS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_USUARIOS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER USUARIOS_BI FOR USUARIOS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_USUARIOS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela USUARIOS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de usuários: {str(e)}")

# Função removida: criar_usuario_padrao()

def listar_usuarios():
    """
    Lista todos os usuários cadastrados no banco
    
    Returns:
        list: Lista de usuários (ID, USUARIO, EMPRESA)
    """
    try:
        query = """
        SELECT ID, USUARIO, EMPRESA FROM USUARIOS
        ORDER BY ID
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        raise Exception(f"Erro ao listar usuários: {str(e)}")

def verificar_tabela_empresas():
    """
    Verifica se a tabela EMPRESAS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'EMPRESAS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela EMPRESAS não encontrada. Criando...")
            query_create = """
            CREATE TABLE EMPRESAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME_EMPRESA VARCHAR(100) NOT NULL,
                NOME_PESSOA VARCHAR(100),
                DOCUMENTO VARCHAR(20) NOT NULL,
                TIPO_DOCUMENTO CHAR(4) NOT NULL,
                REGIME VARCHAR(20),
                TELEFONE VARCHAR(20),
                CEP VARCHAR(10),
                RUA VARCHAR(100),
                NUMERO VARCHAR(10),
                BAIRRO VARCHAR(50),
                CIDADE VARCHAR(50),
                ESTADO CHAR(2)
            )
            """
            execute_query(query_create)
            print("Tabela EMPRESAS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_EMPRESAS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER EMPRESAS_BI FOR EMPRESAS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_EMPRESAS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela EMPRESAS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de empresas: {str(e)}")

def listar_empresas():
    """
    Lista todas as empresas cadastradas
    
    Returns:
        list: Lista de tuplas com dados das empresas (ID, NOME_EMPRESA, DOCUMENTO)
    """
    try:
        query = """
        SELECT ID, NOME_EMPRESA, DOCUMENTO
        FROM EMPRESAS
        ORDER BY ID
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar empresas: {e}")
        raise Exception(f"Erro ao listar empresas: {str(e)}")

def buscar_empresa_por_id(id_empresa):
    """
    Busca uma empresa pelo ID
    
    Args:
        id_empresa (int): ID da empresa
        
    Returns:
        tuple: Dados da empresa ou None se não encontrada
    """
    try:
        query = """
        SELECT * FROM EMPRESAS
        WHERE ID = ?
        """
        result = execute_query(query, (id_empresa,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar empresa: {e}")
        raise Exception(f"Erro ao buscar empresa: {str(e)}")

def buscar_empresa_por_documento(documento):
    """
    Busca uma empresa pelo documento (CNPJ/CPF)
    
    Args:
        documento (str): Documento a buscar (apenas números)
        
    Returns:
        tuple: Dados da empresa ou None se não encontrada
    """
    try:
        # Remover caracteres não numéricos para busca
        documento_limpo = ''.join(filter(str.isdigit, str(documento)))
        
        query = """
        SELECT * FROM EMPRESAS
        WHERE DOCUMENTO = ?
        """
        result = execute_query(query, (documento_limpo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar empresa por documento: {e}")
        raise Exception(f"Erro ao buscar empresa por documento: {str(e)}")

def criar_empresa(nome_empresa, nome_pessoa, documento, tipo_documento, regime, 
                 telefone, cep, rua, numero, bairro, cidade, estado):
    """
    Cria uma nova empresa no banco de dados
    """
    try:
        # Depuração: Imprimir valores recebidos
        print("\n--- Dados recebidos para inserção ---")
        print(f"nome_empresa: '{nome_empresa}' (tipo: {type(nome_empresa)})")
        print(f"nome_pessoa: '{nome_pessoa}' (tipo: {type(nome_pessoa)})")
        print(f"documento: '{documento}' (tipo: {type(documento)})")
        print(f"tipo_documento: '{tipo_documento}' (tipo: {type(tipo_documento)})")
        print(f"regime: '{regime}' (tipo: {type(regime)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"numero: '{numero}' (tipo: {type(numero)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        
        # Remover caracteres não numéricos do documento
        documento_limpo = ''.join(filter(str.isdigit, str(documento))) if documento else ""
        
        # Verificar se já existe uma empresa com o mesmo documento
        if documento_limpo:
            empresa_existente = buscar_empresa_por_documento(documento_limpo)
            if empresa_existente:
                raise Exception(f"Já existe uma empresa cadastrada com este {tipo_documento}")
        
        # Obter o próximo ID
        query_nextid = """
        SELECT COALESCE(MAX(ID), 0) + 1 FROM EMPRESAS
        """
        next_id = execute_query(query_nextid)[0][0]
        
        # Sanitizar e limitar tamanho dos campos - tratamento mais rigoroso
        nome_empresa = str(nome_empresa or "").strip()[:100]
        nome_pessoa = str(nome_pessoa or "").strip()[:100]
        documento_limpo = str(documento_limpo).strip()[:20]
        tipo_documento = str(tipo_documento or "CNPJ").strip()[:4]
        regime = str(regime or "").strip()[:20]
        telefone = str(''.join(filter(str.isdigit, str(telefone))) if telefone else "").strip()[:20]
        cep = str(''.join(filter(str.isdigit, str(cep))) if cep else "").strip()[:10]
        rua = str(rua or "").strip()[:100]
        numero = str(numero or "").strip()[:10]
        bairro = str(bairro or "").strip()[:50]
        cidade = str(cidade or "").strip()[:50]
        estado = str(estado or "").strip().upper()[:2]
        
        # Após o tratamento, imprimir novamente os valores
        print("\n--- Dados tratados para inserção ---")
        print(f"ID: {next_id} (tipo: {type(next_id)})")
        print(f"nome_empresa: '{nome_empresa}' (tipo: {type(nome_empresa)})")
        print(f"nome_pessoa: '{nome_pessoa}' (tipo: {type(nome_pessoa)})")
        print(f"documento_limpo: '{documento_limpo}' (tipo: {type(documento_limpo)})")
        print(f"tipo_documento: '{tipo_documento}' (tipo: {type(tipo_documento)})")
        print(f"regime: '{regime}' (tipo: {type(regime)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"numero: '{numero}' (tipo: {type(numero)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        
        # Inserir a empresa
        query = """
        INSERT INTO EMPRESAS (
            ID, NOME_EMPRESA, NOME_PESSOA, DOCUMENTO, TIPO_DOCUMENTO, 
            REGIME, TELEFONE, CEP, RUA, NUMERO, BAIRRO, CIDADE, ESTADO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            next_id, nome_empresa, nome_pessoa, documento_limpo, tipo_documento,
            regime, telefone, cep, rua, numero, bairro, cidade, estado
        )
        
        # Verificar se algum dos parâmetros é None
        for i, param in enumerate(params):
            if param is None:
                params_list = list(params)
                params_list[i] = ""
                params = tuple(params_list)
                print(f"AVISO: Parâmetro na posição {i} era None, foi substituído por string vazia")
        
        execute_query(query, params)
        
        return next_id
    except Exception as e:
        print(f"Erro ao criar empresa: {e}")
        raise Exception(f"Erro ao criar empresa: {str(e)}")

def atualizar_empresa(id_empresa, nome_empresa, nome_pessoa, documento, tipo_documento, 
                     regime, telefone, cep, rua, numero, bairro, cidade, estado):
    """
    Atualiza os dados de uma empresa existente
    
    Args:
        id_empresa (int): ID da empresa a ser atualizada
        nome_empresa (str): Nome da empresa
        nome_pessoa (str): Nome da pessoa
        documento (str): CNPJ ou CPF (apenas números)
        tipo_documento (str): Tipo do documento ("CNPJ" ou "CPF")
        regime (str): Regime tributário
        telefone (str): Telefone
        cep (str): CEP
        rua (str): Rua/Logradouro
        numero (str): Número
        bairro (str): Bairro
        cidade (str): Cidade
        estado (str): Estado (UF)
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Depuração: Imprimir valores recebidos
        print("\n--- Dados recebidos para atualização ---")
        print(f"id_empresa: {id_empresa} (tipo: {type(id_empresa)})")
        print(f"nome_empresa: '{nome_empresa}' (tipo: {type(nome_empresa)})")
        print(f"nome_pessoa: '{nome_pessoa}' (tipo: {type(nome_pessoa)})")
        print(f"documento: '{documento}' (tipo: {type(documento)})")
        print(f"tipo_documento: '{tipo_documento}' (tipo: {type(tipo_documento)})")
        print(f"regime: '{regime}' (tipo: {type(regime)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"numero: '{numero}' (tipo: {type(numero)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        
        # Remover caracteres não numéricos do documento
        documento_limpo = ''.join(filter(str.isdigit, str(documento))) if documento else ""
        
        # Verificar se a empresa existe
        empresa = buscar_empresa_por_id(id_empresa)
        if not empresa:
            raise Exception(f"Empresa com ID {id_empresa} não encontrada")
        
        # Verificar se outra empresa já usa este documento
        empresa_por_doc = buscar_empresa_por_documento(documento_limpo)
        if empresa_por_doc and empresa_por_doc[0] != id_empresa:
            raise Exception(f"Já existe outra empresa cadastrada com este {tipo_documento}")
        
        # Sanitizar e limitar tamanho dos campos
        nome_empresa = str(nome_empresa or "").strip()[:100]
        nome_pessoa = str(nome_pessoa or "").strip()[:100]
        documento_limpo = str(documento_limpo).strip()[:20]
        tipo_documento = str(tipo_documento or "CNPJ").strip()[:4]
        regime = str(regime or "").strip()[:20]
        telefone = str(''.join(filter(str.isdigit, str(telefone))) if telefone else "").strip()[:20]
        cep = str(''.join(filter(str.isdigit, str(cep))) if cep else "").strip()[:10]
        rua = str(rua or "").strip()[:100]
        numero = str(numero or "").strip()[:10]
        bairro = str(bairro or "").strip()[:50]
        cidade = str(cidade or "").strip()[:50]
        estado = str(estado or "").strip().upper()[:2]
        
        # Após o tratamento, imprimir novamente os valores
        print("\n--- Dados tratados para atualização ---")
        print(f"id_empresa: {id_empresa} (tipo: {type(id_empresa)})")
        print(f"nome_empresa: '{nome_empresa}' (tipo: {type(nome_empresa)})")
        print(f"nome_pessoa: '{nome_pessoa}' (tipo: {type(nome_pessoa)})")
        print(f"documento_limpo: '{documento_limpo}' (tipo: {type(documento_limpo)})")
        print(f"tipo_documento: '{tipo_documento}' (tipo: {type(tipo_documento)})")
        print(f"regime: '{regime}' (tipo: {type(regime)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"numero: '{numero}' (tipo: {type(numero)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        
        # Atualizar a empresa
        query = """
        UPDATE EMPRESAS SET
            NOME_EMPRESA = ?,
            NOME_PESSOA = ?,
            DOCUMENTO = ?,
            TIPO_DOCUMENTO = ?,
            REGIME = ?,
            TELEFONE = ?,
            CEP = ?,
            RUA = ?,
            NUMERO = ?,
            BAIRRO = ?,
            CIDADE = ?,
            ESTADO = ?
        WHERE ID = ?
        """
        
        params = (
            nome_empresa, nome_pessoa, documento_limpo, tipo_documento,
            regime, telefone, cep, rua, numero, bairro, cidade, estado,
            id_empresa
        )
        
        # Verificar se algum dos parâmetros é None
        for i, param in enumerate(params):
            if param is None:
                params_list = list(params)
                params_list[i] = ""
                params = tuple(params_list)
                print(f"AVISO: Parâmetro na posição {i} era None, foi substituído por string vazia")
        
        execute_query(query, params)
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar empresa: {e}")
        raise Exception(f"Erro ao atualizar empresa: {str(e)}")

def excluir_empresa(id_empresa):
    """
    Exclui uma empresa do banco de dados
    
    Args:
        id_empresa (int): ID da empresa a ser excluída
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se a empresa existe
        empresa = buscar_empresa_por_id(id_empresa)
        if not empresa:
            raise Exception(f"Empresa com ID {id_empresa} não encontrada")
        
        # Excluir a empresa
        query = """
        DELETE FROM EMPRESAS
        WHERE ID = ?
        """
        execute_query(query, (id_empresa,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir empresa: {e}")
        raise Exception(f"Erro ao excluir empresa: {str(e)}")

def testar_insercao_simples():
    """
    Função para testar inserção com valores simples e verificar se o banco de dados está funcionando corretamente
    """
    # try:
    #     print("\n--- TESTE DE INSERÇÃO SIMPLES ---")
    #     criar_empresa(
    #         "Empresa Teste", 
    #         "Nome Teste",
    #         "00000000000000",
    #         "CNPJ",
    #         "Simples Nacional",
    #         "0000000000",
    #         "00000000",
    #         "Rua Teste",
    #         "123",
    #         "Bairro Teste",
    #         "Cidade Teste",
    #         "SP"
    #     )
    #     print("Teste de inserção simples concluído com sucesso!")
    # except Exception as e:
    #     print(f"Erro no teste de inserção simples: {e}")

# Adicione estas funções ao seu arquivo banco.py

def verificar_tabela_pessoas():
    """
    Verifica se a tabela PESSOAS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'PESSOAS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela PESSOAS não encontrada. Criando...")
            query_create = """
            CREATE TABLE PESSOAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(100) NOT NULL,
                TIPO_PESSOA CHAR(8) NOT NULL,
                DOCUMENTO VARCHAR(20) NOT NULL,
                TELEFONE VARCHAR(20),
                DATA_CADASTRO DATE,
                CEP VARCHAR(10),
                RUA VARCHAR(100),
                BAIRRO VARCHAR(50),
                CIDADE VARCHAR(50),
                ESTADO CHAR(2),
                OBSERVACAO VARCHAR(200)
            )
            """
            execute_query(query_create)
            print("Tabela PESSOAS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_PESSOAS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER PESSOAS_BI FOR PESSOAS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_PESSOAS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela PESSOAS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de pessoas: {str(e)}")

def listar_pessoas():
    """
    Lista todas as pessoas cadastradas
    
    Returns:
        list: Lista de tuplas com dados das pessoas (ID, NOME, TIPO_PESSOA)
    """
    try:
        query = """
        SELECT ID, NOME, TIPO_PESSOA
        FROM PESSOAS
        ORDER BY ID
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar pessoas: {e}")
        raise Exception(f"Erro ao listar pessoas: {str(e)}")

def buscar_pessoa_por_id(id_pessoa):
    """
    Busca uma pessoa pelo ID
    
    Args:
        id_pessoa (int): ID da pessoa
        
    Returns:
        tuple: Dados da pessoa ou None se não encontrada
    """
    try:
        query = """
        SELECT * FROM PESSOAS
        WHERE ID = ?
        """
        result = execute_query(query, (id_pessoa,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar pessoa: {e}")
        raise Exception(f"Erro ao buscar pessoa: {str(e)}")

def buscar_pessoa_por_documento(documento):
    """
    Busca uma pessoa pelo documento (CNPJ/CPF)
    
    Args:
        documento (str): Documento a buscar (apenas números)
        
    Returns:
        tuple: Dados da pessoa ou None se não encontrada
    """
    try:
        # Remover caracteres não numéricos para busca
        documento_limpo = ''.join(filter(str.isdigit, str(documento)))
        
        query = """
        SELECT * FROM PESSOAS
        WHERE DOCUMENTO = ?
        """
        result = execute_query(query, (documento_limpo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar pessoa por documento: {e}")
        raise Exception(f"Erro ao buscar pessoa por documento: {str(e)}")

def criar_pessoa(nome, tipo_pessoa, documento, telefone, data_cadastro,
               cep, rua, bairro, cidade, estado, observacao=None):
    """
    Cria uma nova pessoa no banco de dados
    """
    try:
        # Depuração: Imprimir valores recebidos
        print("\n--- Dados recebidos para inserção de pessoa ---")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"documento: '{documento}' (tipo: {type(documento)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Remover caracteres não numéricos do documento
        documento_limpo = ''.join(filter(str.isdigit, str(documento))) if documento else ""
        
        # Verificar se já existe uma pessoa com o mesmo documento
        if documento_limpo:
            pessoa_existente = buscar_pessoa_por_documento(documento_limpo)
            if pessoa_existente:
                raise Exception(f"Já existe uma pessoa cadastrada com este documento")
        
        # Obter o próximo ID
        query_nextid = """
        SELECT COALESCE(MAX(ID), 0) + 1 FROM PESSOAS
        """
        next_id = execute_query(query_nextid)[0][0]
        
        # Sanitizar e limitar tamanho dos campos
        nome = str(nome or "").strip()[:100]
        tipo_pessoa = str(tipo_pessoa or "Física").strip()[:8]
        documento_limpo = str(documento_limpo).strip()[:20]
        telefone = str(''.join(filter(str.isdigit, str(telefone))) if telefone else "").strip()[:20]
        cep = str(''.join(filter(str.isdigit, str(cep))) if cep else "").strip()[:10]
        rua = str(rua or "").strip()[:100]
        bairro = str(bairro or "").strip()[:50]
        cidade = str(cidade or "").strip()[:50]
        estado = str(estado or "").strip().upper()[:2]
        observacao = str(observacao or "").strip()[:200]
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_cadastro, str):
            # Assumindo formato dd/mm/yyyy
            try:
                from datetime import datetime
                partes = data_cadastro.split('/')
                if len(partes) == 3:
                    data_cadastro = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_cadastro = None
        
        # Após o tratamento, imprimir novamente os valores
        print("\n--- Dados tratados para inserção de pessoa ---")
        print(f"ID: {next_id} (tipo: {type(next_id)})")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"documento_limpo: '{documento_limpo}' (tipo: {type(documento_limpo)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Inserir a pessoa
        query = """
        INSERT INTO PESSOAS (
            ID, NOME, TIPO_PESSOA, DOCUMENTO, TELEFONE, 
            DATA_CADASTRO, CEP, RUA, BAIRRO, CIDADE, ESTADO, OBSERVACAO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            next_id, nome, tipo_pessoa, documento_limpo, telefone,
            data_cadastro, cep, rua, bairro, cidade, estado, observacao
        )
        
        # Verificar se algum dos parâmetros é None
        for i, param in enumerate(params):
            if param is None and i != 5 and i != 11:  # DATA_CADASTRO e OBSERVACAO podem ser None
                params_list = list(params)
                params_list[i] = ""
                params = tuple(params_list)
                print(f"AVISO: Parâmetro na posição {i} era None, foi substituído por string vazia")
        
        execute_query(query, params)
        
        return next_id
    except Exception as e:
        print(f"Erro ao criar pessoa: {e}")
        raise Exception(f"Erro ao criar pessoa: {str(e)}")

def atualizar_pessoa(id_pessoa, nome, tipo_pessoa, documento, telefone, data_cadastro,
                   cep, rua, bairro, cidade, estado, observacao=None):
    """
    Atualiza os dados de uma pessoa existente
    """
    try:
        # Depuração: Imprimir valores recebidos
        print("\n--- Dados recebidos para atualização de pessoa ---")
        print(f"id_pessoa: {id_pessoa} (tipo: {type(id_pessoa)})")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"documento: '{documento}' (tipo: {type(documento)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Remover caracteres não numéricos do documento
        documento_limpo = ''.join(filter(str.isdigit, str(documento))) if documento else ""
        
        # Verificar se a pessoa existe
        pessoa = buscar_pessoa_por_id(id_pessoa)
        if not pessoa:
            raise Exception(f"Pessoa com ID {id_pessoa} não encontrada")
        
        # Verificar se outra pessoa já usa este documento
        pessoa_por_doc = buscar_pessoa_por_documento(documento_limpo)
        if pessoa_por_doc and pessoa_por_doc[0] != id_pessoa:
            raise Exception(f"Já existe outra pessoa cadastrada com este documento")
        
        # Sanitizar e limitar tamanho dos campos
        nome = str(nome or "").strip()[:100]
        tipo_pessoa = str(tipo_pessoa or "Física").strip()[:8]
        documento_limpo = str(documento_limpo).strip()[:20]
        telefone = str(''.join(filter(str.isdigit, str(telefone))) if telefone else "").strip()[:20]
        cep = str(''.join(filter(str.isdigit, str(cep))) if cep else "").strip()[:10]
        rua = str(rua or "").strip()[:100]
        bairro = str(bairro or "").strip()[:50]
        cidade = str(cidade or "").strip()[:50]
        estado = str(estado or "").strip().upper()[:2]
        observacao = str(observacao or "").strip()[:200]
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_cadastro, str):
            # Assumindo formato dd/mm/yyyy
            try:
                from datetime import datetime
                partes = data_cadastro.split('/')
                if len(partes) == 3:
                    data_cadastro = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_cadastro = None
        
        # Após o tratamento, imprimir novamente os valores
        print("\n--- Dados tratados para atualização de pessoa ---")
        print(f"id_pessoa: {id_pessoa} (tipo: {type(id_pessoa)})")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"documento_limpo: '{documento_limpo}' (tipo: {type(documento_limpo)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Atualizar a pessoa
        query = """
        UPDATE PESSOAS SET
            NOME = ?,
            TIPO_PESSOA = ?,
            DOCUMENTO = ?,
            TELEFONE = ?,
            DATA_CADASTRO = ?,
            CEP = ?,
            RUA = ?,
            BAIRRO = ?,
            CIDADE = ?,
            ESTADO = ?,
            OBSERVACAO = ?
        WHERE ID = ?
        """
        
        params = (
            nome, tipo_pessoa, documento_limpo, telefone, data_cadastro,
            cep, rua, bairro, cidade, estado, observacao, id_pessoa
        )
        
        # Verificar se algum dos parâmetros é None
        for i, param in enumerate(params):
            if param is None and i != 4 and i != 10:  # DATA_CADASTRO e OBSERVACAO podem ser None
                params_list = list(params)
                params_list[i] = ""
                params = tuple(params_list)
                print(f"AVISO: Parâmetro na posição {i} era None, foi substituído por string vazia")
        
        execute_query(query, params)
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar pessoa: {e}")
        raise Exception(f"Erro ao atualizar pessoa: {str(e)}")

def excluir_pessoa(id_pessoa):
    """
    Exclui uma pessoa do banco de dados
    
    Args:
        id_pessoa (int): ID da pessoa a ser excluída
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se a pessoa existe
        pessoa = buscar_pessoa_por_id(id_pessoa)
        if not pessoa:
            raise Exception(f"Pessoa com ID {id_pessoa} não encontrada")
        
        # Excluir a pessoa
        query = """
        DELETE FROM PESSOAS
        WHERE ID = ?
        """
        execute_query(query, (id_pessoa,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir pessoa: {e}")
        raise Exception(f"Erro ao excluir pessoa: {str(e)}")

# Adicione estas funções ao seu arquivo banco.py

def verificar_tabela_funcionarios():
    """
    Verifica se a tabela FUNCIONARIOS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'FUNCIONARIOS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela FUNCIONARIOS não encontrada. Criando...")
            query_create = """
            CREATE TABLE FUNCIONARIOS (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(100) NOT NULL,
                TIPO_VENDEDOR VARCHAR(15) NOT NULL,
                TELEFONE VARCHAR(20),
                TIPO_PESSOA CHAR(8),
                DATA_CADASTRO DATE,
                CPF_CNPJ VARCHAR(20),
                SEXO VARCHAR(10),
                CEP VARCHAR(10),
                RUA VARCHAR(100),
                BAIRRO VARCHAR(50),
                CIDADE VARCHAR(50),
                ESTADO CHAR(2),
                OBSERVACAO VARCHAR(200)
            )
            """
            execute_query(query_create)
            print("Tabela FUNCIONARIOS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_FUNCIONARIOS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER FUNCIONARIOS_BI FOR FUNCIONARIOS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_FUNCIONARIOS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela FUNCIONARIOS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de funcionários: {str(e)}")

def listar_funcionarios():
    """
    Lista todos os funcionários cadastrados
    
    Returns:
        list: Lista de tuplas com dados dos funcionários (ID, NOME, TIPO_VENDEDOR, TELEFONE)
    """
    try:
        query = """
        SELECT ID, NOME, TIPO_VENDEDOR, TELEFONE
        FROM FUNCIONARIOS
        ORDER BY ID
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar funcionários: {e}")
        raise Exception(f"Erro ao listar funcionários: {str(e)}")

def buscar_funcionario_por_id(id_funcionario):
    """
    Busca um funcionário pelo ID
    
    Args:
        id_funcionario (int): ID do funcionário
        
    Returns:
        tuple: Dados do funcionário ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM FUNCIONARIOS
        WHERE ID = ?
        """
        result = execute_query(query, (id_funcionario,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar funcionário: {e}")
        raise Exception(f"Erro ao buscar funcionário: {str(e)}")

def buscar_funcionario_por_cpf_cnpj(cpf_cnpj):
    """
    Busca um funcionário pelo CPF/CNPJ
    
    Args:
        cpf_cnpj (str): CPF/CNPJ a buscar (apenas números)
        
    Returns:
        tuple: Dados do funcionário ou None se não encontrado
    """
    try:
        # Remover caracteres não numéricos para busca
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, str(cpf_cnpj)))
        
        query = """
        SELECT * FROM FUNCIONARIOS
        WHERE CPF_CNPJ = ?
        """
        result = execute_query(query, (cpf_cnpj_limpo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar funcionário por CPF/CNPJ: {e}")
        raise Exception(f"Erro ao buscar funcionário por CPF/CNPJ: {str(e)}")

def criar_funcionario(nome, tipo_vendedor, telefone, tipo_pessoa, data_cadastro,
                    cpf_cnpj, sexo, cep, rua, bairro, cidade, estado, observacao=None):
    """
    Cria um novo funcionário no banco de dados
    """
    try:
        # Depuração: Imprimir valores recebidos
        print("\n--- Dados recebidos para inserção de funcionário ---")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_vendedor: '{tipo_vendedor}' (tipo: {type(tipo_vendedor)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cpf_cnpj: '{cpf_cnpj}' (tipo: {type(cpf_cnpj)})")
        print(f"sexo: '{sexo}' (tipo: {type(sexo)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Remover caracteres não numéricos do CPF/CNPJ
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, str(cpf_cnpj))) if cpf_cnpj else ""
        
        # Verificar se já existe um funcionário com o mesmo CPF/CNPJ
        if cpf_cnpj_limpo:
            funcionario_existente = buscar_funcionario_por_cpf_cnpj(cpf_cnpj_limpo)
            if funcionario_existente:
                documento_tipo = "CPF" if len(cpf_cnpj_limpo) <= 11 else "CNPJ"
                raise Exception(f"Já existe um funcionário cadastrado com este {documento_tipo}")
        
        # Obter o próximo ID
        query_nextid = """
        SELECT COALESCE(MAX(ID), 0) + 1 FROM FUNCIONARIOS
        """
        next_id = execute_query(query_nextid)[0][0]
        
        # Sanitizar e limitar tamanho dos campos
        nome = str(nome or "").strip()[:100]
        tipo_vendedor = str(tipo_vendedor or "Interno").strip()[:15]
        telefone = str(''.join(filter(str.isdigit, str(telefone))) if telefone else "").strip()[:20]
        tipo_pessoa = str(tipo_pessoa or "Física").strip()[:8]
        cpf_cnpj_limpo = str(cpf_cnpj_limpo).strip()[:20]
        sexo = str(sexo or "").strip()[:10]
        cep = str(''.join(filter(str.isdigit, str(cep))) if cep else "").strip()[:10]
        rua = str(rua or "").strip()[:100]
        bairro = str(bairro or "").strip()[:50]
        cidade = str(cidade or "").strip()[:50]
        estado = str(estado or "").strip().upper()[:2]
        observacao = str(observacao or "").strip()[:200]
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_cadastro, str):
            # Assumindo formato dd/mm/yyyy
            try:
                from datetime import datetime
                partes = data_cadastro.split('/')
                if len(partes) == 3:
                    data_cadastro = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_cadastro = None
        
        # Após o tratamento, imprimir novamente os valores
        print("\n--- Dados tratados para inserção de funcionário ---")
        print(f"ID: {next_id} (tipo: {type(next_id)})")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_vendedor: '{tipo_vendedor}' (tipo: {type(tipo_vendedor)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cpf_cnpj_limpo: '{cpf_cnpj_limpo}' (tipo: {type(cpf_cnpj_limpo)})")
        print(f"sexo: '{sexo}' (tipo: {type(sexo)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Inserir o funcionário
        query = """
        INSERT INTO FUNCIONARIOS (
            ID, NOME, TIPO_VENDEDOR, TELEFONE, TIPO_PESSOA, 
            DATA_CADASTRO, CPF_CNPJ, SEXO, CEP, RUA, BAIRRO, CIDADE, ESTADO, OBSERVACAO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            next_id, nome, tipo_vendedor, telefone, tipo_pessoa,
            data_cadastro, cpf_cnpj_limpo, sexo, cep, rua, bairro, cidade, estado, observacao
        )
        
        # Verificar se algum dos parâmetros é None
        for i, param in enumerate(params):
            if param is None and i != 5 and i != 13:  # DATA_CADASTRO e OBSERVACAO podem ser None
                params_list = list(params)
                params_list[i] = ""
                params = tuple(params_list)
                print(f"AVISO: Parâmetro na posição {i} era None, foi substituído por string vazia")
        
        execute_query(query, params)
        
        return next_id
    except Exception as e:
        print(f"Erro ao criar funcionário: {e}")
        raise Exception(f"Erro ao criar funcionário: {str(e)}")

def atualizar_funcionario(id_funcionario, nome, tipo_vendedor, telefone, tipo_pessoa, data_cadastro,
                        cpf_cnpj, sexo, cep, rua, bairro, cidade, estado, observacao=None):
    """
    Atualiza os dados de um funcionário existente
    """
    try:
        # Depuração: Imprimir valores recebidos
        print("\n--- Dados recebidos para atualização de funcionário ---")
        print(f"id_funcionario: {id_funcionario} (tipo: {type(id_funcionario)})")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_vendedor: '{tipo_vendedor}' (tipo: {type(tipo_vendedor)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cpf_cnpj: '{cpf_cnpj}' (tipo: {type(cpf_cnpj)})")
        print(f"sexo: '{sexo}' (tipo: {type(sexo)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Remover caracteres não numéricos do CPF/CNPJ
        cpf_cnpj_limpo = ''.join(filter(str.isdigit, str(cpf_cnpj))) if cpf_cnpj else ""
        
        # Verificar se o funcionário existe
        funcionario = buscar_funcionario_por_id(id_funcionario)
        if not funcionario:
            raise Exception(f"Funcionário com ID {id_funcionario} não encontrado")
        
        # Verificar se outro funcionário já usa este CPF/CNPJ
        if cpf_cnpj_limpo:
            funcionario_por_doc = buscar_funcionario_por_cpf_cnpj(cpf_cnpj_limpo)
            if funcionario_por_doc and funcionario_por_doc[0] != id_funcionario:
                documento_tipo = "CPF" if len(cpf_cnpj_limpo) <= 11 else "CNPJ"
                raise Exception(f"Já existe outro funcionário cadastrado com este {documento_tipo}")
        
        # Sanitizar e limitar tamanho dos campos
        nome = str(nome or "").strip()[:100]
        tipo_vendedor = str(tipo_vendedor or "Interno").strip()[:15]
        telefone = str(''.join(filter(str.isdigit, str(telefone))) if telefone else "").strip()[:20]
        tipo_pessoa = str(tipo_pessoa or "Física").strip()[:8]
        cpf_cnpj_limpo = str(cpf_cnpj_limpo).strip()[:20]
        sexo = str(sexo or "").strip()[:10]
        cep = str(''.join(filter(str.isdigit, str(cep))) if cep else "").strip()[:10]
        rua = str(rua or "").strip()[:100]
        bairro = str(bairro or "").strip()[:50]
        cidade = str(cidade or "").strip()[:50]
        estado = str(estado or "").strip().upper()[:2]
        observacao = str(observacao or "").strip()[:200]
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_cadastro, str):
            # Assumindo formato dd/mm/yyyy
            try:
                from datetime import datetime
                partes = data_cadastro.split('/')
                if len(partes) == 3:
                    data_cadastro = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_cadastro = None
        
        # Após o tratamento, imprimir novamente os valores
        print("\n--- Dados tratados para atualização de funcionário ---")
        print(f"id_funcionario: {id_funcionario} (tipo: {type(id_funcionario)})")
        print(f"nome: '{nome}' (tipo: {type(nome)})")
        print(f"tipo_vendedor: '{tipo_vendedor}' (tipo: {type(tipo_vendedor)})")
        print(f"telefone: '{telefone}' (tipo: {type(telefone)})")
        print(f"tipo_pessoa: '{tipo_pessoa}' (tipo: {type(tipo_pessoa)})")
        print(f"data_cadastro: '{data_cadastro}' (tipo: {type(data_cadastro)})")
        print(f"cpf_cnpj_limpo: '{cpf_cnpj_limpo}' (tipo: {type(cpf_cnpj_limpo)})")
        print(f"sexo: '{sexo}' (tipo: {type(sexo)})")
        print(f"cep: '{cep}' (tipo: {type(cep)})")
        print(f"rua: '{rua}' (tipo: {type(rua)})")
        print(f"bairro: '{bairro}' (tipo: {type(bairro)})")
        print(f"cidade: '{cidade}' (tipo: {type(cidade)})")
        print(f"estado: '{estado}' (tipo: {type(estado)})")
        print(f"observacao: '{observacao}' (tipo: {type(observacao)})")
        
        # Atualizar o funcionário
        query = """
        UPDATE FUNCIONARIOS SET
            NOME = ?,
            TIPO_VENDEDOR = ?,
            TELEFONE = ?,
            TIPO_PESSOA = ?,
            DATA_CADASTRO = ?,
            CPF_CNPJ = ?,
            SEXO = ?,
            CEP = ?,
            RUA = ?,
            BAIRRO = ?,
            CIDADE = ?,
            ESTADO = ?,
            OBSERVACAO = ?
        WHERE ID = ?
        """
        
        params = (
            nome, tipo_vendedor, telefone, tipo_pessoa, data_cadastro,
            cpf_cnpj_limpo, sexo, cep, rua, bairro, cidade, estado, observacao,
            id_funcionario
        )
        
        # Verificar se algum dos parâmetros é None
        for i, param in enumerate(params):
            if param is None and i != 4 and i != 12:  # DATA_CADASTRO e OBSERVACAO podem ser None
                params_list = list(params)
                params_list[i] = ""
                params = tuple(params_list)
                print(f"AVISO: Parâmetro na posição {i} era None, foi substituído por string vazia")
        
        execute_query(query, params)
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar funcionário: {e}")
        raise Exception(f"Erro ao atualizar funcionário: {str(e)}")

def excluir_funcionario(id_funcionario):
    """
    Exclui um funcionário do banco de dados
    
    Args:
        id_funcionario (int): ID do funcionário a ser excluído
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se o funcionário existe
        funcionario = buscar_funcionario_por_id(id_funcionario)
        if not funcionario:
            raise Exception(f"Funcionário com ID {id_funcionario} não encontrado")
        
        # Excluir o funcionário
        query = """
        DELETE FROM FUNCIONARIOS
        WHERE ID = ?
        """
        execute_query(query, (id_funcionario,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir funcionário: {e}")
        raise Exception(f"Erro ao excluir funcionário: {str(e)}")

# Adicione estas funções ao arquivo banco.py

def verificar_tabela_produtos():
    """
    Verifica se a tabela PRODUTOS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'PRODUTOS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela PRODUTOS não encontrada. Criando...")
            query_create = """
            CREATE TABLE PRODUTOS (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(20) NOT NULL,
                NOME VARCHAR(100) NOT NULL,
                CODIGO_BARRAS VARCHAR(50),
                MARCA VARCHAR(50),
                GRUPO VARCHAR(50),
                PRECO_CUSTO DECIMAL(10,2),
                PRECO_VENDA DECIMAL(10,2),
                QUANTIDADE_ESTOQUE INTEGER,
                UNIQUE (CODIGO)
            )
            """
            execute_query(query_create)
            print("Tabela PRODUTOS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_PRODUTOS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER PRODUTOS_BI FOR PRODUTOS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_PRODUTOS_ID, 1);
                    END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela PRODUTOS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de produtos: {str(e)}")

def listar_produtos():
    """
    Lista todos os produtos cadastrados
    
    Returns:
        list: Lista de tuplas com dados dos produtos
    """
    try:
        query = """
        SELECT ID, CODIGO, NOME, CODIGO_BARRAS, MARCA, GRUPO,
               PRECO_CUSTO, PRECO_VENDA, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        ORDER BY CODIGO
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar produtos: {e}")
        raise Exception(f"Erro ao listar produtos: {str(e)}")

def buscar_produto_por_id(id_produto):
    """
    Busca um produto pelo ID
    
    Args:
        id_produto (int): ID do produto
        
    Returns:
        tuple: Dados do produto ou None se não encontrado
    """
    try:
        query = """
        SELECT ID, CODIGO, NOME, CODIGO_BARRAS, MARCA, GRUPO,
               PRECO_CUSTO, PRECO_VENDA, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        WHERE ID = ?
        """
        result = execute_query(query, (id_produto,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar produto: {e}")
        raise Exception(f"Erro ao buscar produto: {str(e)}")

def buscar_produto_por_codigo(codigo):
    """
    Busca um produto pelo código
    
    Args:
        codigo (str): Código do produto
        
    Returns:
        tuple: Dados do produto ou None se não encontrado
    """
    try:
        query = """
        SELECT ID, CODIGO, NOME, CODIGO_BARRAS, MARCA, GRUPO,
               PRECO_CUSTO, PRECO_VENDA, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        WHERE CODIGO = ?
        """
        result = execute_query(query, (codigo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar produto por código: {e}")
        raise Exception(f"Erro ao buscar produto por código: {str(e)}")

def criar_produto(codigo, nome, codigo_barras=None, marca=None, grupo=None, 
                preco_custo=0, preco_venda=0, quantidade_estoque=0):
    """
    Cria um novo produto no banco de dados
    
    Args:
        codigo (str): Código do produto
        nome (str): Nome do produto
        codigo_barras (str, optional): Código de barras
        marca (str, optional): Marca do produto
        grupo (str, optional): Grupo/categoria do produto
        preco_custo (float, optional): Preço de custo
        preco_venda (float, optional): Preço de venda
        quantidade_estoque (int, optional): Quantidade em estoque
    
    Returns:
        int: ID do produto criado
    """
    try:
        # Verificar se já existe um produto com o mesmo código
        produto_existente = buscar_produto_por_codigo(codigo)
        if produto_existente:
            raise Exception(f"Já existe um produto cadastrado com o código {codigo}")
        
        # Sanitizar e converter dados
        codigo = str(codigo).strip()[:20]
        nome = str(nome).strip()[:100]
        codigo_barras = str(codigo_barras).strip()[:50] if codigo_barras else None
        marca = str(marca).strip()[:50] if marca else None
        grupo = str(grupo).strip()[:50] if grupo and grupo != "Selecione um grupo" else None
        
        # Garantir que os valores numéricos são do tipo correto
        try:
            preco_custo = float(preco_custo) if preco_custo else 0
            preco_venda = float(preco_venda) if preco_venda else 0
            quantidade_estoque = int(quantidade_estoque) if quantidade_estoque else 0
        except (ValueError, TypeError):
            preco_custo = 0
            preco_venda = 0
            quantidade_estoque = 0
        
        # Inserir o produto
        query = """
        INSERT INTO PRODUTOS (
            CODIGO, NOME, CODIGO_BARRAS, MARCA, GRUPO,
            PRECO_CUSTO, PRECO_VENDA, QUANTIDADE_ESTOQUE
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            codigo, nome, codigo_barras, marca, grupo,
            preco_custo, preco_venda, quantidade_estoque
        )
        
        execute_query(query, params)
        
        # Retornar o ID do produto inserido
        produto_inserido = buscar_produto_por_codigo(codigo)
        if produto_inserido:
            return produto_inserido[0]  # ID é o primeiro item da tupla
        
        return None
    except Exception as e:
        print(f"Erro ao criar produto: {e}")
        raise Exception(f"Erro ao criar produto: {str(e)}")

def atualizar_produto(id_produto, codigo, nome, codigo_barras=None, marca=None, grupo=None, 
                    preco_custo=0, preco_venda=0, quantidade_estoque=0):
    """
    Atualiza um produto existente
    
    Args:
        id_produto (int): ID do produto a ser atualizado
        codigo (str): Código do produto
        nome (str): Nome do produto
        codigo_barras (str, optional): Código de barras
        marca (str, optional): Marca do produto
        grupo (str, optional): Grupo/categoria do produto
        preco_custo (float, optional): Preço de custo
        preco_venda (float, optional): Preço de venda
        quantidade_estoque (int, optional): Quantidade em estoque
    
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se o produto existe
        produto = buscar_produto_por_id(id_produto)
        if not produto:
            raise Exception(f"Produto com ID {id_produto} não encontrado")
        
        # Verificar se o código sendo alterado já está em uso
        if codigo != produto[1]:  # Comparar com o código atual (índice 1)
            produto_existente = buscar_produto_por_codigo(codigo)
            if produto_existente:
                raise Exception(f"Já existe outro produto com o código {codigo}")
        
        # Sanitizar e converter dados
        codigo = str(codigo).strip()[:20]
        nome = str(nome).strip()[:100]
        codigo_barras = str(codigo_barras).strip()[:50] if codigo_barras else None
        marca = str(marca).strip()[:50] if marca else None
        grupo = str(grupo).strip()[:50] if grupo and grupo != "Selecione um grupo" else None
        
        # Garantir que os valores numéricos são do tipo correto
        try:
            preco_custo = float(preco_custo) if preco_custo is not None else 0
            preco_venda = float(preco_venda) if preco_venda is not None else 0
            quantidade_estoque = int(quantidade_estoque) if quantidade_estoque is not None else 0
        except (ValueError, TypeError):
            preco_custo = 0
            preco_venda = 0
            quantidade_estoque = 0
        
        # Atualizar o produto
        query = """
        UPDATE PRODUTOS SET
            CODIGO = ?,
            NOME = ?,
            CODIGO_BARRAS = ?,
            MARCA = ?,
            GRUPO = ?,
            PRECO_CUSTO = ?,
            PRECO_VENDA = ?,
            QUANTIDADE_ESTOQUE = ?
        WHERE ID = ?
        """
        
        params = (
            codigo, nome, codigo_barras, marca, grupo,
            preco_custo, preco_venda, quantidade_estoque,
            id_produto
        )
        
        execute_query(query, params)
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar produto: {e}")
        raise Exception(f"Erro ao atualizar produto: {str(e)}")

def excluir_produto(id_produto):
    """
    Exclui um produto do banco de dados
    
    Args:
        id_produto (int): ID do produto a ser excluído
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se o produto existe
        produto = buscar_produto_por_id(id_produto)
        if not produto:
            raise Exception(f"Produto com ID {id_produto} não encontrado")
        
        # Excluir o produto
        query = """
        DELETE FROM PRODUTOS
        WHERE ID = ?
        """
        execute_query(query, (id_produto,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir produto: {e}")
        raise Exception(f"Erro ao excluir produto: {str(e)}")

def buscar_produto_por_barras(codigo_barras):
    """
    Busca um produto pelo código de barras
    
    Args:
        codigo_barras (str): Código de barras do produto
        
    Returns:
        dict: Dicionário com dados do produto ou None se não encontrado
    """
    try:
        query = """
        SELECT ID, CODIGO, NOME, CODIGO_BARRAS, MARCA, GRUPO,
               PRECO_CUSTO, PRECO_VENDA, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        WHERE CODIGO_BARRAS = ?
        """
        result = execute_query(query, (codigo_barras,))
        if result and len(result) > 0:
            # Converter para dicionário para facilitar o acesso
            produto = {
                "id": result[0][0],
                "codigo": result[0][1],
                "nome": result[0][2],
                "barras": result[0][3],
                "marca": result[0][4],
                "grupo": result[0][5],
                "preco_compra": result[0][6],
                "preco_venda": result[0][7],
                "estoque": result[0][8]
            }
            return produto
        return None
    except Exception as e:
        print(f"Erro ao buscar produto por código de barras: {e}")
        return None
    
def buscar_produtos_por_filtro(codigo="", nome="", codigo_barras="", grupo="", marca=""):
    """
    Busca produtos no banco de dados com base em filtros específicos
    
    Args:
        codigo (str, optional): Código do produto
        nome (str, optional): Nome do produto (busca parcial)
        codigo_barras (str, optional): Código de barras do produto
        grupo (str, optional): Grupo/categoria do produto
        marca (str, optional): Marca do produto
        
    Returns:
        list: Lista de produtos que correspondem aos filtros
    """
    try:
        # Construir consulta SQL base
        query = """
        SELECT ID, CODIGO, NOME, CODIGO_BARRAS, MARCA, GRUPO,
               PRECO_CUSTO, PRECO_VENDA, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        WHERE 1=1
        """
        
        # Lista para armazenar os parâmetros de filtro
        params = []
        
        # Adicionar condições conforme os filtros fornecidos
        if codigo:
            query += " AND CODIGO = ?"
            params.append(codigo)
            
        if nome:
            query += " AND UPPER(NOME) LIKE UPPER(?)"
            params.append(f"%{nome}%")  # Busca parcial, case-insensitive
            
        if codigo_barras:
            query += " AND CODIGO_BARRAS = ?"
            params.append(codigo_barras)
            
        if grupo:
            query += " AND UPPER(GRUPO) = UPPER(?)"
            params.append(grupo)
            
        if marca:
            query += " AND UPPER(MARCA) = UPPER(?)"
            params.append(marca)
        
        # Adicionar ordenação
        query += " ORDER BY CODIGO"
        
        # Executar a consulta
        from base.banco import execute_query
        result = execute_query(query, tuple(params) if params else None)
        
        return result
    except Exception as e:
        print(f"Erro ao buscar produtos por filtro: {e}")
        raise Exception(f"Erro ao buscar produtos: {str(e)}")
# Adicione estas funções ao arquivo banco.py

def verificar_tabela_marcas():
    """
    Verifica se a tabela MARCAS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'MARCAS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela MARCAS não encontrada. Criando...")
            query_create = """
            CREATE TABLE MARCAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(50) NOT NULL,
                UNIQUE (NOME)
            )
            """
            execute_query(query_create)
            print("Tabela MARCAS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_MARCAS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER MARCAS_BI FOR MARCAS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_MARCAS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            # Adicionar marcas iniciais
            marcas_iniciais = ["Nestlé", "Unilever", "Procter & Gamble", "Coca-Cola", 
                              "Camil", "Dell", "Samsung", "Lacoste", "OMO"]
            for marca in marcas_iniciais:
                try:
                    query_insert = "INSERT INTO MARCAS (NOME) VALUES (?)"
                    execute_query(query_insert, (marca,))
                except Exception as e:
                    print(f"Aviso ao inserir marca inicial {marca}: {e}")
            
            return True
        else:
            print("Tabela MARCAS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de marcas: {str(e)}")

def verificar_tabela_grupos():
    """
    Verifica se a tabela GRUPOS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'GRUPOS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela GRUPOS não encontrada. Criando...")
            query_create = """
            CREATE TABLE GRUPOS (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(50) NOT NULL,
                UNIQUE (NOME)
            )
            """
            execute_query(query_create)
            print("Tabela GRUPOS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_GRUPOS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER GRUPOS_BI FOR GRUPOS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_GRUPOS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            # Adicionar grupos iniciais
            grupos_iniciais = ["Alimentos", "Bebidas", "Limpeza", "Higiene", 
                             "Hortifruti", "Eletrônicos", "Vestuário", "Outros"]
            for grupo in grupos_iniciais:
                try:
                    query_insert = "INSERT INTO GRUPOS (NOME) VALUES (?)"
                    execute_query(query_insert, (grupo,))
                except Exception as e:
                    print(f"Aviso ao inserir grupo inicial {grupo}: {e}")
            
            return True
        else:
            print("Tabela GRUPOS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de grupos: {str(e)}")

def listar_marcas():
    """
    Lista todas as marcas cadastradas
    
    Returns:
        list: Lista de marcas
    """
    try:
        query = """
        SELECT NOME FROM MARCAS
        ORDER BY NOME
        """
        result = execute_query(query)
        # Converter resultado para lista simples
        marcas = [marca[0] for marca in result]
        return marcas
    except Exception as e:
        print(f"Erro ao listar marcas: {e}")
        raise Exception(f"Erro ao listar marcas: {str(e)}")

def listar_grupos():
    """
    Lista todos os grupos cadastrados
    
    Returns:
        list: Lista de grupos
    """
    try:
        query = """
        SELECT NOME FROM GRUPOS
        ORDER BY NOME
        """
        result = execute_query(query)
        # Converter resultado para lista simples
        grupos = [grupo[0] for grupo in result]
        return grupos
    except Exception as e:
        print(f"Erro ao listar grupos: {e}")
        raise Exception(f"Erro ao listar grupos: {str(e)}")

def adicionar_marca(nome):
    """
    Adiciona uma nova marca
    
    Args:
        nome (str): Nome da marca
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se já existe uma marca com este nome
        query_check = """
        SELECT COUNT(*) FROM MARCAS
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome,))
        
        if result[0][0] > 0:
            print(f"Marca '{nome}' já existe")
            return False
        
        # Inserir a nova marca
        query_insert = """
        INSERT INTO MARCAS (NOME) VALUES (?)
        """
        execute_query(query_insert, (nome,))
        print(f"Marca '{nome}' adicionada com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao adicionar marca: {e}")
        raise Exception(f"Erro ao adicionar marca: {str(e)}")

def atualizar_marca(nome_antigo, nome_novo):
    """
    Atualiza o nome de uma marca
    
    Args:
        nome_antigo (str): Nome atual da marca
        nome_novo (str): Novo nome da marca
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se a marca existe
        query_check = """
        SELECT COUNT(*) FROM MARCAS
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome_antigo,))
        
        if result[0][0] == 0:
            print(f"Marca '{nome_antigo}' não encontrada")
            return False
        
        # Verificar se o novo nome já existe (ignorando caso)
        if nome_antigo.upper() != nome_novo.upper():
            result = execute_query(query_check, (nome_novo,))
            if result[0][0] > 0:
                print(f"Já existe uma marca com o nome '{nome_novo}'")
                return False
        
        # Atualizar a marca
        query_update = """
        UPDATE MARCAS
        SET NOME = ?
        WHERE UPPER(NOME) = UPPER(?)
        """
        execute_query(query_update, (nome_novo, nome_antigo))
        
        # Também atualizar os produtos que usam esta marca
        query_update_produtos = """
        UPDATE PRODUTOS
        SET MARCA = ?
        WHERE UPPER(MARCA) = UPPER(?)
        """
        execute_query(query_update_produtos, (nome_novo, nome_antigo))
        
        print(f"Marca atualizada de '{nome_antigo}' para '{nome_novo}'")
        return True
    except Exception as e:
        print(f"Erro ao atualizar marca: {e}")
        raise Exception(f"Erro ao atualizar marca: {str(e)}")

def excluir_marca(nome):
    """
    Exclui uma marca
    
    Args:
        nome (str): Nome da marca a ser excluída
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se a marca existe
        query_check = """
        SELECT COUNT(*) FROM MARCAS
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome,))
        
        if result[0][0] == 0:
            print(f"Marca '{nome}' não encontrada")
            return False
        
        # Verificar se há produtos com esta marca
        query_check_produtos = """
        SELECT COUNT(*) FROM PRODUTOS
        WHERE UPPER(MARCA) = UPPER(?)
        """
        result = execute_query(query_check_produtos, (nome,))
        
        if result[0][0] > 0:
            # Atualizar produtos para remover a marca
            query_update_produtos = """
            UPDATE PRODUTOS
            SET MARCA = NULL
            WHERE UPPER(MARCA) = UPPER(?)
            """
            execute_query(query_update_produtos, (nome,))
            print(f"Atualizado {result[0][0]} produtos que usavam a marca '{nome}'")
        
        # Excluir a marca
        query_delete = """
        DELETE FROM MARCAS
        WHERE UPPER(NOME) = UPPER(?)
        """
        execute_query(query_delete, (nome,))
        
        print(f"Marca '{nome}' excluída com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao excluir marca: {e}")
        raise Exception(f"Erro ao excluir marca: {str(e)}")

def adicionar_grupo(nome):
    """
    Adiciona um novo grupo
    
    Args:
        nome (str): Nome do grupo
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se já existe um grupo com este nome
        query_check = """
        SELECT COUNT(*) FROM GRUPOS
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome,))
        
        if result[0][0] > 0:
            print(f"Grupo '{nome}' já existe")
            return False
        
        # Inserir o novo grupo
        query_insert = """
        INSERT INTO GRUPOS (NOME) VALUES (?)
        """
        execute_query(query_insert, (nome,))
        
        print(f"Grupo '{nome}' adicionado com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao adicionar grupo: {e}")
        raise Exception(f"Erro ao adicionar grupo: {str(e)}")

def atualizar_grupo(nome_antigo, nome_novo):
    """
    Atualiza o nome de um grupo
    
    Args:
        nome_antigo (str): Nome atual do grupo
        nome_novo (str): Novo nome do grupo
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se o grupo existe
        query_check = """
        SELECT COUNT(*) FROM GRUPOS
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome_antigo,))
        
        if result[0][0] == 0:
            print(f"Grupo '{nome_antigo}' não encontrado")
            return False
        
        # Verificar se o novo nome já existe (ignorando caso)
        if nome_antigo.upper() != nome_novo.upper():
            result = execute_query(query_check, (nome_novo,))
            if result[0][0] > 0:
                print(f"Já existe um grupo com o nome '{nome_novo}'")
                return False
        
        # Atualizar o grupo
        query_update = """
        UPDATE GRUPOS
        SET NOME = ?
        WHERE UPPER(NOME) = UPPER(?)
        """
        execute_query(query_update, (nome_novo, nome_antigo))
        
        # Também atualizar os produtos que usam este grupo
        query_update_produtos = """
        UPDATE PRODUTOS
        SET GRUPO = ?
        WHERE UPPER(GRUPO) = UPPER(?)
        """
        execute_query(query_update_produtos, (nome_novo, nome_antigo))
        
        print(f"Grupo atualizado de '{nome_antigo}' para '{nome_novo}'")
        return True
    except Exception as e:
        print(f"Erro ao atualizar grupo: {e}")
        raise Exception(f"Erro ao atualizar grupo: {str(e)}")

def excluir_grupo(nome):
    """
    Exclui um grupo
    
    Args:
        nome (str): Nome do grupo a ser excluído
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se o grupo existe
        query_check = """
        SELECT COUNT(*) FROM GRUPOS
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome,))
        
        if result[0][0] == 0:
            print(f"Grupo '{nome}' não encontrado")
            return False
        
        # Verificar se há produtos com este grupo
        query_check_produtos = """
        SELECT COUNT(*) FROM PRODUTOS
        WHERE UPPER(GRUPO) = UPPER(?)
        """
        result = execute_query(query_check_produtos, (nome,))
        
        if result[0][0] > 0:
            # Atualizar produtos para remover o grupo
            query_update_produtos = """
            UPDATE PRODUTOS
            SET GRUPO = NULL
            WHERE UPPER(GRUPO) = UPPER(?)
            """
            execute_query(query_update_produtos, (nome,))
            print(f"Atualizado {result[0][0]} produtos que usavam o grupo '{nome}'")
        
        # Excluir o grupo
        query_delete = """
        DELETE FROM GRUPOS
        WHERE UPPER(NOME) = UPPER(?)
        """
        execute_query(query_delete, (nome,))
        
        print(f"Grupo '{nome}' excluído com sucesso")
        return True
    except Exception as e:
        print(f"Erro ao excluir grupo: {e}")
        raise Exception(f"Erro ao excluir grupo: {str(e)}")



def verificar_tabela_fornecedores():
    """
    Verifica se a tabela FORNECEDORES existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'FORNECEDORES'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela FORNECEDORES não encontrada. Criando...")
            query_create = """
            CREATE TABLE FORNECEDORES (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(20) NOT NULL,
                NOME VARCHAR(100) NOT NULL,
                FANTASIA VARCHAR(100),
                TIPO VARCHAR(20),
                CNPJ VARCHAR(20),
                DATA_CADASTRO DATE,
                CEP VARCHAR(10),
                RUA VARCHAR(100),
                BAIRRO VARCHAR(50),
                CIDADE VARCHAR(50),
                ESTADO CHAR(2),
                UNIQUE (CODIGO)
            )
            """
            execute_query(query_create)
            print("Tabela FORNECEDORES criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_FORNECEDORES_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER FORNECEDORES_BI FOR FORNECEDORES
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_FORNECEDORES_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela FORNECEDORES já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de fornecedores: {str(e)}")

def listar_fornecedores():
    """
    Lista todos os fornecedores cadastrados
    
    Returns:
        list: Lista de tuplas com dados dos fornecedores
    """
    try:
        query = """
        SELECT ID, CODIGO, NOME, FANTASIA, TIPO
        FROM FORNECEDORES
        ORDER BY CODIGO
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar fornecedores: {e}")
        raise Exception(f"Erro ao listar fornecedores: {str(e)}")

def buscar_fornecedor_por_id(id_fornecedor):
    """
    Busca um fornecedor pelo ID
    
    Args:
        id_fornecedor (int): ID do fornecedor
        
    Returns:
        tuple: Dados do fornecedor ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM FORNECEDORES
        WHERE ID = ?
        """
        result = execute_query(query, (id_fornecedor,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar fornecedor: {e}")
        raise Exception(f"Erro ao buscar fornecedor: {str(e)}")

def buscar_fornecedor_por_codigo(codigo):
    """
    Busca um fornecedor pelo código
    
    Args:
        codigo (str): Código do fornecedor
        
    Returns:
        tuple: Dados do fornecedor ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM FORNECEDORES
        WHERE CODIGO = ?
        """
        result = execute_query(query, (codigo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar fornecedor por código: {e}")
        raise Exception(f"Erro ao buscar fornecedor por código: {str(e)}")

def buscar_fornecedor_por_cnpj(cnpj):
    """
    Busca um fornecedor pelo CNPJ
    
    Args:
        cnpj (str): CNPJ do fornecedor (apenas números)
        
    Returns:
        tuple: Dados do fornecedor ou None se não encontrado
    """
    try:
        # Remover caracteres não numéricos para busca
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
        
        query = """
        SELECT * FROM FORNECEDORES
        WHERE CNPJ = ?
        """
        result = execute_query(query, (cnpj_limpo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar fornecedor por CNPJ: {e}")
        raise Exception(f"Erro ao buscar fornecedor por CNPJ: {str(e)}")

def criar_fornecedor(codigo, nome, fantasia=None, tipo=None, cnpj=None, 
                    data_cadastro=None, cep=None, rua=None, bairro=None, 
                    cidade=None, estado=None):
    """
    Cria um novo fornecedor no banco de dados
    
    Args:
        codigo (str): Código do fornecedor (será gerado automaticamente pelo banco)
        nome (str): Nome do fornecedor
        fantasia (str, optional): Nome fantasia
        tipo (str, optional): Tipo do fornecedor
        cnpj (str, optional): CNPJ do fornecedor
        data_cadastro (date, optional): Data de cadastro
        cep (str, optional): CEP
        rua (str, optional): Rua/Logradouro
        bairro (str, optional): Bairro
        cidade (str, optional): Cidade
        estado (str, optional): Estado (UF)
    
    Returns:
        int: ID do fornecedor criado
    """
    try:
        # Gerar código automático baseado no próximo ID
        query_nextid = """
        SELECT COALESCE(MAX(ID), 0) + 1 FROM FORNECEDORES
        """
        next_id = execute_query(query_nextid)[0][0]
        codigo_gerado = str(next_id)  # Usamos o ID como código
        
        # Sanitizar e converter dados
        nome = str(nome).strip()[:100]
        fantasia = str(fantasia).strip()[:100] if fantasia else None
        tipo = str(tipo).strip()[:20] if tipo and tipo != "Selecione um tipo" else None
        
        # Tratar CNPJ - remover caracteres não numéricos
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj))) if cnpj else None
        
        # Verificar se já existe um fornecedor com o mesmo CNPJ
        if cnpj_limpo:
            fornecedor_por_cnpj = buscar_fornecedor_por_cnpj(cnpj_limpo)
            if fornecedor_por_cnpj:
                raise Exception(f"Já existe um fornecedor cadastrado com este CNPJ")
        
        # Sanitizar demais campos
        cep = ''.join(filter(str.isdigit, str(cep))) if cep else None
        rua = str(rua).strip()[:100] if rua else None
        bairro = str(bairro).strip()[:50] if bairro else None
        cidade = str(cidade).strip()[:50] if cidade else None
        estado = str(estado).strip().upper()[:2] if estado else None
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_cadastro, str):
            # Assumindo formato dd/mm/yyyy
            try:
                from datetime import datetime
                partes = data_cadastro.split('/')
                if len(partes) == 3:
                    data_cadastro = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_cadastro = None
        
        # Inserir o fornecedor com o código gerado
        query = """
        INSERT INTO FORNECEDORES (
            CODIGO, NOME, FANTASIA, TIPO, CNPJ,
            DATA_CADASTRO, CEP, RUA, BAIRRO, CIDADE, ESTADO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            codigo_gerado, nome, fantasia, tipo, cnpj_limpo,
            data_cadastro, cep, rua, bairro, cidade, estado
        )
        
        execute_query(query, params)
        
        # Retornar o ID do fornecedor inserido
        fornecedor_inserido = buscar_fornecedor_por_codigo(codigo_gerado)
        if fornecedor_inserido:
            return fornecedor_inserido[0]  # ID é o primeiro item da tupla
        
        return None
    except Exception as e:
        print(f"Erro ao criar fornecedor: {e}")
        raise Exception(f"Erro ao criar fornecedor: {str(e)}")


# Ajuste para o formulario_fornecedores.py - Modificar a cor do texto nas mensagens
# Substitua o método mostrar_mensagem na classe TiposFornecedoresDialog

def mostrar_mensagem(self, titulo, texto):
    """Exibe uma caixa de mensagem"""
    msg_box = QMessageBox()
    if "Aviso" in titulo:
        msg_box.setIcon(QMessageBox.Warning)
    elif "Erro" in titulo:
        msg_box.setIcon(QMessageBox.Critical)
    else:
        msg_box.setIcon(QMessageBox.Information)
    
    msg_box.setWindowTitle(titulo)
    msg_box.setText(texto)
    msg_box.setStyleSheet("""
        QMessageBox { 
            background-color: white;
        }
        QLabel { 
            color: white;  /* Alterado para branco */
            background-color: #003b57; /* Cor de fundo escura para contraste */
        }
        QPushButton {
            background-color: #003b57;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 2px;
        }
    """)
    msg_box.exec_()

# Ajuste para o método incluir na classe FormularioFornecedores
# Substituir a parte que cria um novo fornecedor

def incluir(self):
    """Inclui um novo fornecedor ou atualiza um existente"""
    # Validar campos obrigatórios
    nome = self.nome_input.text()
    fantasia = self.fantasia_input.text()
    tipo_index = self.tipo_combo.currentIndex()
    documento = self.documento_input.text()
    
    if not nome or tipo_index == 0 or not documento:
        self.mostrar_mensagem("Atenção", "Preencha todos os campos obrigatórios (Nome, Tipo e Documento)!")
        return
    
    # Obter o tipo de pessoa e definir o código
    tipo_pessoa = "Jurídica" if self.tipo_pessoa_combo.currentIndex() == 0 else "Física"
    tipo = self.tipo_combo.currentText()
    
    # Obter os dados complementares
    cep = self.cep_input.text()
    rua = self.rua_input.text()
    bairro = self.bairro_input.text()
    cidade = self.cidade_input.text()
    estado = self.estado_input.text()
    
    # Obter a data de cadastro
    data_cadastro = self.data_input.date().toString("dd/MM/yyyy")
    
    try:
        # Verificar se é inclusão ou atualização
        if self.fornecedor_id is None:
            # Criar novo fornecedor - o código será gerado automaticamente pelo método criar_fornecedor
            id_fornecedor = criar_fornecedor(
                # Passamos uma string vazia e o banco gerará o código
                "",
                nome, fantasia, tipo, documento, data_cadastro,
                cep, rua, bairro, cidade, estado
            )
            
            mensagem = "Fornecedor incluído com sucesso!"
        else:
            # Para atualização, precisamos obter o código existente
            fornecedor_existente = buscar_fornecedor_por_id(self.fornecedor_id)
            codigo_existente = fornecedor_existente[1] if fornecedor_existente else ""
            
            # Atualizar fornecedor existente
            atualizar_fornecedor(
                self.fornecedor_id, codigo_existente, nome, fantasia, tipo, documento, 
                data_cadastro, cep, rua, bairro, cidade, estado
            )
            
            mensagem = "Fornecedor atualizado com sucesso!"
        
        # Recarregar a tabela da tela de cadastro
        if self.cadastro_tela and hasattr(self.cadastro_tela, 'carregar_fornecedores'):
            self.cadastro_tela.carregar_fornecedores()
        
        # Mostrar mensagem de sucesso
        self.mostrar_mensagem("Sucesso", mensagem)
        
        # Fechar a janela de formulário após a inclusão
        if self.janela_parent:
            self.janela_parent.close()
            
    except Exception as e:
        print(f"Erro ao salvar fornecedor: {e}")
        self.mostrar_mensagem("Erro", f"Não foi possível salvar o fornecedor: {str(e)}")

def atualizar_fornecedor(id_fornecedor, codigo, nome, fantasia=None, tipo=None, cnpj=None, 
                        data_cadastro=None, cep=None, rua=None, bairro=None, 
                        cidade=None, estado=None):
    """
    Atualiza um fornecedor existente
    
    Args:
        id_fornecedor (int): ID do fornecedor a ser atualizado
        codigo (str): Código do fornecedor
        nome (str): Nome do fornecedor
        fantasia (str, optional): Nome fantasia
        tipo (str, optional): Tipo do fornecedor
        cnpj (str, optional): CNPJ do fornecedor
        data_cadastro (date, optional): Data de cadastro
        cep (str, optional): CEP
        rua (str, optional): Rua/Logradouro
        bairro (str, optional): Bairro
        cidade (str, optional): Cidade
        estado (str, optional): Estado (UF)
    
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se o fornecedor existe
        fornecedor = buscar_fornecedor_por_id(id_fornecedor)
        if not fornecedor:
            raise Exception(f"Fornecedor com ID {id_fornecedor} não encontrado")
        
        # Verificar se o código sendo alterado já está em uso
        if codigo != fornecedor[1]:  # Comparar com o código atual (índice 1)
            fornecedor_existente = buscar_fornecedor_por_codigo(codigo)
            if fornecedor_existente:
                raise Exception(f"Já existe outro fornecedor com o código {codigo}")
        
        # Sanitizar e converter dados
        codigo = str(codigo).strip()[:20]
        nome = str(nome).strip()[:100]
        fantasia = str(fantasia).strip()[:100] if fantasia else None
        tipo = str(tipo).strip()[:20] if tipo and tipo != "Selecione um tipo" else None
        
        # Tratar CNPJ - remover caracteres não numéricos
        cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj))) if cnpj else None
        
        # Verificar se outro fornecedor já usa este CNPJ
        if cnpj_limpo:
            fornecedor_por_cnpj = buscar_fornecedor_por_cnpj(cnpj_limpo)
            if fornecedor_por_cnpj and fornecedor_por_cnpj[0] != id_fornecedor:
                raise Exception(f"Já existe outro fornecedor cadastrado com este CNPJ")
        
        # Sanitizar demais campos
        cep = ''.join(filter(str.isdigit, str(cep))) if cep else None
        rua = str(rua).strip()[:100] if rua else None
        bairro = str(bairro).strip()[:50] if bairro else None
        cidade = str(cidade).strip()[:50] if cidade else None
        estado = str(estado).strip().upper()[:2] if estado else None
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_cadastro, str):
            # Assumindo formato dd/mm/yyyy
            try:
                from datetime import datetime
                partes = data_cadastro.split('/')
                if len(partes) == 3:
                    data_cadastro = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_cadastro = None
        
        # Atualizar o fornecedor
        query = """
        UPDATE FORNECEDORES SET
            CODIGO = ?,
            NOME = ?,
            FANTASIA = ?,
            TIPO = ?,
            CNPJ = ?,
            DATA_CADASTRO = ?,
            CEP = ?,
            RUA = ?,
            BAIRRO = ?,
            CIDADE = ?,
            ESTADO = ?
        WHERE ID = ?
        """
        
        params = (
            codigo, nome, fantasia, tipo, cnpj_limpo,
            data_cadastro, cep, rua, bairro, cidade, estado,
            id_fornecedor
        )
        
        execute_query(query, params)
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar fornecedor: {e}")
        raise Exception(f"Erro ao atualizar fornecedor: {str(e)}")

def excluir_fornecedor(id_fornecedor):
    """
    Exclui um fornecedor do banco de dados
    
    Args:
        id_fornecedor (int): ID do fornecedor a ser excluído
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se o fornecedor existe
        fornecedor = buscar_fornecedor_por_id(id_fornecedor)
        if not fornecedor:
            raise Exception(f"Fornecedor com ID {id_fornecedor} não encontrado")
        
        # Excluir o fornecedor
        query = """
        DELETE FROM FORNECEDORES
        WHERE ID = ?
        """
        execute_query(query, (id_fornecedor,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir fornecedor: {e}")
        raise Exception(f"Erro ao excluir fornecedor: {str(e)}")


if __name__ == "__main__":
    try:
        print(f"Iniciando configuração do banco de dados: {DB_PATH}")
        verificar_tabela_usuarios()
        verificar_tabela_empresas()
        verificar_tabela_pessoas()
        verificar_tabela_funcionarios()
        verificar_tabela_produtos()
        verificar_tabela_marcas()  # Nova tabela
        verificar_tabela_grupos()  # Nova tabela
        verificar_tabela_fornecedores()
        print("Banco de dados inicializado com sucesso!")
        
        # ...
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {str(e)}")

def buscar_fornecedores_por_filtro(codigo="", nome="", cnpj="", tipo=""):
    """
    Busca fornecedores no banco de dados com base em filtros específicos
    
    Args:
        codigo (str, optional): Código do fornecedor
        nome (str, optional): Nome do fornecedor (busca parcial)
        cnpj (str, optional): CNPJ do fornecedor (busca parcial)
        tipo (str, optional): Tipo do fornecedor
        
    Returns:
        list: Lista de fornecedores que correspondem aos filtros
    """
    try:
        # Construir consulta SQL base
        query = """
        SELECT ID, CODIGO, NOME, FANTASIA, TIPO, CNPJ
        FROM FORNECEDORES
        WHERE 1=1
        """
        
        # Lista para armazenar os parâmetros de filtro
        params = []
        
        # Adicionar condições conforme os filtros fornecidos
        if codigo:
            query += " AND CODIGO = ?"
            params.append(codigo)
            
        if nome:
            query += " AND UPPER(NOME) LIKE UPPER(?)"
            params.append(f"%{nome}%")  # Busca parcial, case-insensitive
            
        if cnpj:
            # Remover caracteres não numéricos para busca
            cnpj_limpo = ''.join(filter(str.isdigit, cnpj))
            if cnpj_limpo:
                query += " AND CNPJ LIKE ?"
                params.append(f"%{cnpj_limpo}%")
        
        # Filtrar pelo tipo de fornecedor
        if tipo and tipo != "Todos":
            query += " AND TIPO = ?"
            params.append(tipo)
        
        # Adicionar ordenação
        query += " ORDER BY CODIGO"
        
        # Executar a consulta
        result = execute_query(query, tuple(params) if params else None)
        
        return result
    except Exception as e:
        print(f"Erro ao buscar fornecedores por filtro: {e}")
        raise Exception(f"Erro ao buscar fornecedores: {str(e)}")

def verificar_tabela_tipos_fornecedores():
    """
    Verifica se a tabela TIPOS_FORNECEDORES existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'TIPOS_FORNECEDORES'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela TIPOS_FORNECEDORES não encontrada. Criando...")
            query_create = """
            CREATE TABLE TIPOS_FORNECEDORES (
                ID INTEGER NOT NULL PRIMARY KEY,
                NOME VARCHAR(50) NOT NULL,
                UNIQUE (NOME)
            )
            """
            execute_query(query_create)
            print("Tabela TIPOS_FORNECEDORES criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_TIPOS_FORNECEDORES_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER TIPOS_FORNECEDORES_BI FOR TIPOS_FORNECEDORES
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_TIPOS_FORNECEDORES_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            # Inserir tipos padrão
            tipos_padrao = ["Fabricante", "Distribuidor", "Atacadista", "Varejista", "Importador"]
            for tipo in tipos_padrao:
                try:
                    query_insert = "INSERT INTO TIPOS_FORNECEDORES (NOME) VALUES (?)"
                    execute_query(query_insert, (tipo,))
                    print(f"Tipo '{tipo}' inserido com sucesso.")
                except Exception as e:
                    print(f"Erro ao inserir tipo padrão '{tipo}': {e}")
            
            return True
        else:
            print("Tabela TIPOS_FORNECEDORES já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de tipos de fornecedores: {str(e)}")

def listar_tipos_fornecedores():
    """
    Lista todos os tipos de fornecedores cadastrados
    
    Returns:
        list: Lista de tipos de fornecedores
    """
    try:
        query = """
        SELECT ID, NOME FROM TIPOS_FORNECEDORES
        ORDER BY NOME
        """
        result = execute_query(query)
        return result
    except Exception as e:
        print(f"Erro ao listar tipos de fornecedores: {e}")
        raise Exception(f"Erro ao listar tipos de fornecedores: {str(e)}")

def adicionar_tipo_fornecedor(nome):
    """
    Adiciona um novo tipo de fornecedor
    
    Args:
        nome (str): Nome do tipo de fornecedor
        
    Returns:
        int: ID do tipo adicionado
    """
    try:
        # Verificar se já existe um tipo com esse nome
        query_check = """
        SELECT COUNT(*) FROM TIPOS_FORNECEDORES
        WHERE UPPER(NOME) = UPPER(?)
        """
        result = execute_query(query_check, (nome,))
        
        if result[0][0] > 0:
            raise Exception(f"Já existe um tipo de fornecedor com o nome '{nome}'")
        
        # Inserir novo tipo
        query_insert = """
        INSERT INTO TIPOS_FORNECEDORES (NOME) VALUES (?)
        """
        
        execute_query(query_insert, (nome,))
        
        # Obter o ID pelo nome
        query_get_id = """
        SELECT ID FROM TIPOS_FORNECEDORES
        WHERE NOME = ?
        """
        result = execute_query(query_get_id, (nome,))
        
        if result and len(result) > 0:
            return result[0][0]
        
        return None
    except Exception as e:
        print(f"Erro ao adicionar tipo de fornecedor: {e}")
        raise Exception(f"Erro ao adicionar tipo de fornecedor: {str(e)}")

def atualizar_tipo_fornecedor(id_tipo, novo_nome):
    """
    Atualiza o nome de um tipo de fornecedor
    
    Args:
        id_tipo (int): ID do tipo de fornecedor
        novo_nome (str): Novo nome do tipo
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se já existe outro tipo com esse nome
        query_check = """
        SELECT COUNT(*) FROM TIPOS_FORNECEDORES
        WHERE UPPER(NOME) = UPPER(?) AND ID <> ?
        """
        result = execute_query(query_check, (novo_nome, id_tipo))
        
        if result[0][0] > 0:
            raise Exception(f"Já existe outro tipo de fornecedor com o nome '{novo_nome}'")
        
        # Atualizar o tipo
        query_update = """
        UPDATE TIPOS_FORNECEDORES 
        SET NOME = ?
        WHERE ID = ?
        """
        
        execute_query(query_update, (novo_nome, id_tipo))
        
        # Atualizar fornecedores que usam este tipo (pelo nome antigo)
        query_get_old_name = """
        SELECT NOME FROM TIPOS_FORNECEDORES WHERE ID = ?
        """
        result = execute_query(query_get_old_name, (id_tipo,))
        
        if result and len(result) > 0:
            nome_antigo = result[0][0]
            
            # Atualizar fornecedores
            query_update_fornecedores = """
            UPDATE FORNECEDORES
            SET TIPO = ?
            WHERE TIPO = ?
            """
            execute_query(query_update_fornecedores, (novo_nome, nome_antigo))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar tipo de fornecedor: {e}")
        raise Exception(f"Erro ao atualizar tipo de fornecedor: {str(e)}")

def excluir_tipo_fornecedor(id_tipo):
    """
    Exclui um tipo de fornecedor
    
    Args:
        id_tipo (int): ID do tipo de fornecedor
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se existem fornecedores usando este tipo
        query_get_name = """
        SELECT NOME FROM TIPOS_FORNECEDORES WHERE ID = ?
        """
        result = execute_query(query_get_name, (id_tipo,))
        
        if not result or len(result) == 0:
            raise Exception(f"Tipo de fornecedor com ID {id_tipo} não encontrado")
        
        nome_tipo = result[0][0]
        
        # Verificar uso do tipo
        query_check_uso = """
        SELECT COUNT(*) FROM FORNECEDORES
        WHERE TIPO = ?
        """
        result = execute_query(query_check_uso, (nome_tipo,))
        
        if result[0][0] > 0:
            raise Exception(f"Não é possível excluir o tipo '{nome_tipo}' pois está sendo usado por {result[0][0]} fornecedor(es)")
        
        # Excluir o tipo
        query_delete = """
        DELETE FROM TIPOS_FORNECEDORES
        WHERE ID = ?
        """
        execute_query(query_delete, (id_tipo,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir tipo de fornecedor: {e}")
        raise Exception(f"Erro ao excluir tipo de fornecedor: {str(e)}")

# Adicione estas funções ao seu arquivo banco.py

def verificar_tabela_pedidos_venda():
    """
    Verifica se a tabela PEDIDOS_VENDA existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'PEDIDOS_VENDA'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela PEDIDOS_VENDA não encontrada. Criando...")
            query_create = """
            CREATE TABLE PEDIDOS_VENDA (
                ID INTEGER NOT NULL PRIMARY KEY,
                NUMERO_PEDIDO VARCHAR(20) NOT NULL,
                CLIENTE VARCHAR(100) NOT NULL,
                CLIENTE_ID INTEGER,
                VENDEDOR VARCHAR(100) NOT NULL,
                VENDEDOR_ID INTEGER,
                VALOR DECIMAL(15,2),
                PRODUTO VARCHAR(100),
                PRODUTO_ID INTEGER,
                DATA_PEDIDO DATE,
                CIDADE VARCHAR(50),
                STATUS VARCHAR(20) DEFAULT 'Pendente',
                OBSERVACAO VARCHAR(200),
                UNIQUE (NUMERO_PEDIDO)
            )
            """
            execute_query(query_create)
            print("Tabela PEDIDOS_VENDA criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_PEDIDOS_VENDA_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER PEDIDOS_VENDA_BI FOR PEDIDOS_VENDA
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_PEDIDOS_VENDA_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            return True
        else:
            print("Tabela PEDIDOS_VENDA já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de pedidos de venda: {str(e)}")

def listar_pedidos_venda():
    """
    Lista todos os pedidos de venda cadastrados
    
    Returns:
        list: Lista de tuplas com dados dos pedidos
    """
    try:
        query = """
        SELECT ID, NUMERO_PEDIDO, CLIENTE, VENDEDOR, VALOR, DATA_PEDIDO, STATUS
        FROM PEDIDOS_VENDA
        ORDER BY NUMERO_PEDIDO
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar pedidos de venda: {e}")
        raise Exception(f"Erro ao listar pedidos de venda: {str(e)}")

def buscar_pedido_por_id(id_pedido):
    """
    Busca um pedido pelo ID
    
    Args:
        id_pedido (int): ID do pedido
        
    Returns:
        tuple: Dados do pedido ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM PEDIDOS_VENDA
        WHERE ID = ?
        """
        result = execute_query(query, (id_pedido,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar pedido: {e}")
        raise Exception(f"Erro ao buscar pedido: {str(e)}")

def buscar_pedido_por_numero(numero_pedido):
    """
    Busca um pedido pelo número
    
    Args:
        numero_pedido (str): Número do pedido
        
    Returns:
        tuple: Dados do pedido ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM PEDIDOS_VENDA
        WHERE NUMERO_PEDIDO = ?
        """
        result = execute_query(query, (numero_pedido,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar pedido por número: {e}")
        raise Exception(f"Erro ao buscar pedido por número: {str(e)}")

def gerar_numero_pedido():
    """
    Gera um novo número de pedido sequencial
    
    Returns:
        str: Próximo número de pedido no formato '00001'
    """
    try:
        query = """
        SELECT COALESCE(MAX(ID), 0) + 1 FROM PEDIDOS_VENDA
        """
        result = execute_query(query)
        next_id = result[0][0]
        
        # Formatar o número do pedido com zeros à esquerda (5 dígitos)
        numero_pedido = f"{next_id:05d}"
        return numero_pedido
    except Exception as e:
        print(f"Erro ao gerar número de pedido: {e}")
        raise Exception(f"Erro ao gerar número de pedido: {str(e)}")

def criar_pedido(id=None, cliente=None, cliente_id=None, vendedor=None, vendedor_id=None, 
               valor=None, produto=None, produto_id=None, data_pedido=None, cidade=None, 
               observacao=None, status="Pendente"):
    """
    Cria um novo pedido de venda no banco de dados
    """
    try:
        # Gerar o próximo número de pedido
        numero_pedido = gerar_numero_pedido()
        
        # Gerar ID explícito
        query_id = "SELECT COALESCE(MAX(ID), 0) + 1 FROM PEDIDOS_VENDA"
        proximo_id = execute_query(query_id)[0][0]
        
        # Sanitizar e converter dados
        cliente = str(cliente).strip()[:100]
        vendedor = str(vendedor).strip()[:100]
        produto = str(produto).strip()[:100] if produto else None
        cidade = str(cidade).strip()[:50] if cidade else None
        observacao = str(observacao).strip()[:200] if observacao else None
        status = str(status).strip()[:20] if status else "Pendente"
        
        # Converter valor para float
        try:
            valor_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
            valor_float = float(valor_str)
        except (ValueError, TypeError):
            valor_float = 0
        
        # Converter data para formato do banco (se for string)
        if isinstance(data_pedido, str):
            try:
                from datetime import datetime
                partes = data_pedido.split('/')
                if len(partes) == 3:
                    data_pedido = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                data_pedido = None
        
        # Inserir o pedido com ID explícito
        query = """
        INSERT INTO PEDIDOS_VENDA (
            ID, NUMERO_PEDIDO, CLIENTE, CLIENTE_ID, VENDEDOR, VENDEDOR_ID,
            VALOR, PRODUTO, PRODUTO_ID, DATA_PEDIDO, CIDADE, STATUS, OBSERVACAO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            proximo_id, numero_pedido, cliente, cliente_id, vendedor, vendedor_id,
            valor_float, produto, produto_id, data_pedido, cidade, status, observacao
        )
        
        execute_query(query, params)
        
        return numero_pedido
    except Exception as e:
        print(f"Erro ao criar pedido: {e}")
        raise Exception(f"Erro ao criar pedido: {str(e)}")

def atualizar_pedido(id_pedido, cliente=None, cliente_id=None, vendedor=None, vendedor_id=None, 
                   valor=None, produto=None, produto_id=None, data_pedido=None, cidade=None, 
                   observacao=None, status=None):
    """
    Atualiza um pedido existente
    
    Args:
        id_pedido (int): ID do pedido a ser atualizado
        cliente (str, optional): Nome do cliente
        cliente_id (int, optional): ID do cliente
        vendedor (str, optional): Nome do vendedor
        vendedor_id (int, optional): ID do vendedor
        valor (float, optional): Valor do pedido
        produto (str, optional): Nome do produto
        produto_id (int, optional): ID do produto
        data_pedido (date, optional): Data do pedido
        cidade (str, optional): Cidade do cliente
        observacao (str, optional): Observações adicionais
        status (str, optional): Status do pedido
    
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se o pedido existe
        pedido = buscar_pedido_por_id(id_pedido)
        if not pedido:
            raise Exception(f"Pedido com ID {id_pedido} não encontrado")
        
        # Preparar os campos para atualização
        campos_atualizacao = []
        valores = []
        
        if cliente is not None:
            campos_atualizacao.append("CLIENTE = ?")
            valores.append(str(cliente).strip()[:100])
            
        if cliente_id is not None:
            campos_atualizacao.append("CLIENTE_ID = ?")
            valores.append(cliente_id)
            
        if vendedor is not None:
            campos_atualizacao.append("VENDEDOR = ?")
            valores.append(str(vendedor).strip()[:100])
            
        if vendedor_id is not None:
            campos_atualizacao.append("VENDEDOR_ID = ?")
            valores.append(vendedor_id)
            
        if valor is not None:
            # Converter valor para float
            try:
                # Remover símbolos de moeda e substituir vírgula por ponto
                valor_str = str(valor).replace('R$', '').replace('.', '').replace(',', '.').strip()
                valor_float = float(valor_str)
                campos_atualizacao.append("VALOR = ?")
                valores.append(valor_float)
            except (ValueError, TypeError):
                pass  # Ignora se não for um valor válido
            
        if produto is not None:
            campos_atualizacao.append("PRODUTO = ?")
            valores.append(str(produto).strip()[:100])
            
        if produto_id is not None:
            campos_atualizacao.append("PRODUTO_ID = ?")
            valores.append(produto_id)
            
        if data_pedido is not None:
            # Converter data para formato do banco (se for string)
            if isinstance(data_pedido, str):
                # Assumindo formato dd/mm/yyyy
                try:
                    from datetime import datetime
                    partes = data_pedido.split('/')
                    if len(partes) == 3:
                        data_pedido = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
                except Exception as e:
                    print(f"Erro ao converter data: {e}")
                    data_pedido = None
            
            campos_atualizacao.append("DATA_PEDIDO = ?")
            valores.append(data_pedido)
            
        if cidade is not None:
            campos_atualizacao.append("CIDADE = ?")
            valores.append(str(cidade).strip()[:50])
            
        if observacao is not None:
            campos_atualizacao.append("OBSERVACAO = ?")
            valores.append(str(observacao).strip()[:200])
            
        if status is not None:
            campos_atualizacao.append("STATUS = ?")
            valores.append(str(status).strip()[:20])
        
        # Se não houver campos para atualizar, retorna sucesso
        if not campos_atualizacao:
            return True
        
        # Construir a query de atualização
        query = f"""
        UPDATE PEDIDOS_VENDA SET
            {", ".join(campos_atualizacao)}
        WHERE ID = ?
        """
        
        # Adicionar o ID do pedido aos parâmetros
        valores.append(id_pedido)
        
        execute_query(query, tuple(valores))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar pedido: {e}")
        raise Exception(f"Erro ao atualizar pedido: {str(e)}")

def excluir_pedido(id_pedido):
    """
    Exclui um pedido do banco de dados
    
    Args:
        id_pedido (int): ID do pedido a ser excluído
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se o pedido existe
        pedido = buscar_pedido_por_id(id_pedido)
        if not pedido:
            raise Exception(f"Pedido com ID {id_pedido} não encontrado")
        
        # Excluir o pedido
        query = """
        DELETE FROM PEDIDOS_VENDA
        WHERE ID = ?
        """
        execute_query(query, (id_pedido,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir pedido: {e}")
        raise Exception(f"Erro ao excluir pedido: {str(e)}")

def buscar_pedidos_por_filtro(vendedor="", cliente="", cidade="", data_inicial=None, data_final=None, status=None):
    """
    Busca pedidos de venda no banco de dados com base em filtros específicos
    
    Args:
        vendedor (str, optional): Nome do vendedor (busca parcial)
        cliente (str, optional): Nome do cliente (busca parcial)
        cidade (str, optional): Cidade do cliente (busca parcial)
        data_inicial (date, optional): Data inicial para filtro
        data_final (date, optional): Data final para filtro
        status (str, optional): Status do pedido
        
    Returns:
        list: Lista de pedidos que correspondem aos filtros
    """
    try:
        # Construir consulta SQL base
        query = """
        SELECT ID, NUMERO_PEDIDO, CLIENTE, VENDEDOR, VALOR, DATA_PEDIDO, STATUS
        FROM PEDIDOS_VENDA
        WHERE 1=1
        """
        
        # Lista para armazenar os parâmetros de filtro
        params = []
        
        # Adicionar condições conforme os filtros fornecidos
        if vendedor:
            query += " AND UPPER(VENDEDOR) LIKE UPPER(?)"
            params.append(f"%{vendedor}%")  # Busca parcial, case-insensitive
            
        if cliente:
            query += " AND UPPER(CLIENTE) LIKE UPPER(?)"
            params.append(f"%{cliente}%")  # Busca parcial, case-insensitive
            
        if cidade:
            query += " AND UPPER(CIDADE) LIKE UPPER(?)"
            params.append(f"%{cidade}%")  # Busca parcial, case-insensitive
            
        if data_inicial:
            # Converter data para formato do banco (se for string)
            if isinstance(data_inicial, str):
                # Assumindo formato dd/mm/yyyy
                try:
                    from datetime import datetime
                    partes = data_inicial.split('/')
                    if len(partes) == 3:
                        data_inicial = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
                except Exception as e:
                    print(f"Erro ao converter data inicial: {e}")
                    data_inicial = None
            
            if data_inicial:
                query += " AND DATA_PEDIDO >= ?"
                params.append(data_inicial)
                
        if data_final:
            # Converter data para formato do banco (se for string)
            if isinstance(data_final, str):
                # Assumindo formato dd/mm/yyyy
                try:
                    from datetime import datetime
                    partes = data_final.split('/')
                    if len(partes) == 3:
                        data_final = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
                except Exception as e:
                    print(f"Erro ao converter data final: {e}")
                    data_final = None
            
            if data_final:
                query += " AND DATA_PEDIDO <= ?"
                params.append(data_final)
                
        if status:
            query += " AND UPPER(STATUS) = UPPER(?)"
            params.append(status)
        
        # Adicionar ordenação
        query += " ORDER BY NUMERO_PEDIDO"
        
        # Executar a consulta
        result = execute_query(query, tuple(params) if params else None)
        
        return result
    except Exception as e:
        print(f"Erro ao buscar pedidos por filtro: {e}")
        raise Exception(f"Erro ao buscar pedidos: {str(e)}")

def obter_vendedores_pedidos():
    """
    Obtém lista de vendedores que têm pedidos cadastrados
    
    Returns:
        list: Lista de nomes de vendedores
    """
    try:
        query = """
        SELECT DISTINCT VENDEDOR FROM PEDIDOS_VENDA
        ORDER BY VENDEDOR
        """
        result = execute_query(query)
        return [row[0] for row in result]
    except Exception as e:
        print(f"Erro ao obter vendedores: {e}")
        raise Exception(f"Erro ao obter vendedores: {str(e)}")

def obter_clientes_pedidos():
    """
    Obtém lista de clientes que têm pedidos cadastrados
    
    Returns:
        list: Lista de nomes de clientes
    """
    try:
        query = """
        SELECT DISTINCT CLIENTE FROM PEDIDOS_VENDA
        ORDER BY CLIENTE
        """
        result = execute_query(query)
        return [row[0] for row in result]
    except Exception as e:
        print(f"Erro ao obter clientes: {e}")
        raise Exception(f"Erro ao obter clientes: {str(e)}")

def obter_cidades_pedidos():
    """
    Obtém lista de cidades que têm pedidos cadastrados
    
    Returns:
        list: Lista de nomes de cidades
    """
    try:
        query = """
        SELECT DISTINCT CIDADE FROM PEDIDOS_VENDA
        WHERE CIDADE IS NOT NULL AND CIDADE <> ''
        ORDER BY CIDADE
        """
        result = execute_query(query)
        return [row[0] for row in result]
    except Exception as e:
        print(f"Erro ao obter cidades: {e}")
        raise Exception(f"Erro ao obter cidades: {str(e)}")

# Adicione estas funções ao arquivo base/banco.py

def verificar_tabela_recebimentos_clientes():
    """
    Verifica se a tabela RECEBIMENTOS_CLIENTES existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'RECEBIMENTOS_CLIENTES'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela RECEBIMENTOS_CLIENTES não encontrada. Criando...")
            query_create = """
            CREATE TABLE RECEBIMENTOS_CLIENTES (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(20) NOT NULL,
                CLIENTE VARCHAR(100) NOT NULL,
                CLIENTE_ID INTEGER,
                VENCIMENTO DATE,
                VALOR DECIMAL(15,2) NOT NULL,
                DATA_RECEBIMENTO DATE,
                STATUS VARCHAR(20) DEFAULT 'Pendente'
            )
            """
            execute_query(query_create)
            print("Tabela RECEBIMENTOS_CLIENTES criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_RECEBIMENTOS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                # Se o gerador já existir, ignoramos o erro
                pass
            
            # Criar o trigger para autoincrementar o ID
            try:
                query_trigger = """
                CREATE TRIGGER RECEBIMENTOS_BI FOR RECEBIMENTOS_CLIENTES
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_RECEBIMENTOS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            # Adicionar dados de exemplo
            inserir_dados_exemplo_recebimentos()
            
            return True
        else:
            print("Tabela RECEBIMENTOS_CLIENTES já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de recebimentos: {str(e)}")

def inserir_dados_exemplo_recebimentos():
    """
    Insere dados de exemplo na tabela de recebimentos para teste
    """
    try:
        # Verificar se já existem dados na tabela
        query_check = "SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES"
        result = execute_query(query_check)
        
        if result[0][0] > 0:
            print("Tabela RECEBIMENTOS_CLIENTES já possui dados. Pulando inserção de exemplos.")
            return
        
        # Dados de exemplo
        from datetime import datetime, timedelta
        hoje = datetime.now().date()
        
        # Datas de vencimento (em dias a partir de hoje)
        vencimentos = [1, 5, 10, 15, 30]
        
        dados = [
            ("001", "Empresa ABC Ltda", None, hoje + timedelta(days=vencimentos[0]), 5000.00),
            ("002", "João Silva", None, hoje + timedelta(days=vencimentos[1]), 1200.00),
            ("003", "Distribuidora XYZ", None, hoje + timedelta(days=vencimentos[2]), 3500.00),
            ("004", "Ana Souza", None, hoje + timedelta(days=vencimentos[3]), 750.00),
            ("005", "Mercado Central", None, hoje + timedelta(days=vencimentos[4]), 2100.00)
        ]
        
        # Inserir dados de exemplo
        query_insert = """
        INSERT INTO RECEBIMENTOS_CLIENTES (
            CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, STATUS
        ) VALUES (?, ?, ?, ?, ?, 'Pendente')
        """
        
        for dado in dados:
            execute_query(query_insert, dado)
            
        print("Dados de exemplo inseridos com sucesso na tabela RECEBIMENTOS_CLIENTES.")
    except Exception as e:
        print(f"Erro ao inserir dados de exemplo: {e}")
        # Não propagar o erro, apenas registrar

def listar_recebimentos_pendentes():
    """
    Lista todos os recebimentos pendentes
    
    Returns:
        list: Lista de tuplas com dados dos recebimentos pendentes
    """
    try:
        # Log para depuração
        print("Buscando recebimentos pendentes...")
        
        query = """
        SELECT ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, STATUS, VALOR_ORIGINAL
        FROM RECEBIMENTOS_CLIENTES
        WHERE STATUS = 'Pendente'
        ORDER BY VENCIMENTO
        """
        result = execute_query(query)
        
        # Depuração: mostrar quantos registros foram encontrados
        print(f"Encontrados {len(result) if result else 0} recebimentos pendentes.")
        
        return result
    except Exception as e:
        print(f"Erro ao listar recebimentos pendentes: {e}")
        raise Exception(f"Erro ao listar recebimentos pendentes: {str(e)}")
    

def buscar_recebimento_por_id(id_recebimento):
    """
    Busca um recebimento pelo ID
    
    Args:
        id_recebimento (int): ID do recebimento
        
    Returns:
        tuple: Dados do recebimento ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM RECEBIMENTOS_CLIENTES
        WHERE ID = ?
        """
        result = execute_query(query, (id_recebimento,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar recebimento: {e}")
        raise Exception(f"Erro ao buscar recebimento: {str(e)}")

def dar_baixa_recebimento(id_recebimento, valor_pago, data_pagamento, criar_novo=True):
    """
    Dá baixa em um recebimento
    
    Args:
        id_recebimento (int): ID do recebimento
        valor_pago (float): Valor pago
        data_pagamento (date): Data do pagamento
        criar_novo (bool, optional): Se deve criar um novo registro para o pagamento. Defaults to True.
    """
    try:
        # Se deve criar um novo registro para o pagamento
        if criar_novo:
            # Gerar ID explícito para o registro de pagamento
            query_id = "SELECT COALESCE(MAX(ID), 0) + 1 FROM RECEBIMENTOS_CLIENTES"
            proximo_id = execute_query(query_id)[0][0]
            
            # Buscar dados do recebimento original
            recebimento = buscar_recebimento_por_id(id_recebimento)
            if not recebimento:
                raise Exception(f"Recebimento ID {id_recebimento} não encontrado")
            
            # Extrair dados
            codigo = recebimento[1]
            cliente = recebimento[2]
            cliente_id = recebimento[3]
            
            # Inserir registro de pagamento
            query = """
            INSERT INTO RECEBIMENTOS_CLIENTES (
                ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Recebido')
            """
            
            params = (
                proximo_id, codigo, cliente, cliente_id, data_pagamento, valor_pago, data_pagamento
            )
            
            execute_query(query, params)
            
            # Atualizar status do recebimento original
            query_update = """
            UPDATE RECEBIMENTOS_CLIENTES
            SET STATUS = 'Recebido'
            WHERE ID = ?
            """
            
            execute_query(query_update, (id_recebimento,))
        else:
            # Apenas registrar o pagamento sem criar novo registro
            # Inserir registro de pagamento
            query = """
            INSERT INTO RECEBIMENTOS_CLIENTES (
                CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            ) 
            SELECT CODIGO, CLIENTE, CLIENTE_ID, ?, ?, ?, 'Recebido'
            FROM RECEBIMENTOS_CLIENTES
            WHERE ID = ?
            """
            
            execute_query(query, (data_pagamento, valor_pago, data_pagamento, id_recebimento))
            
        return True
    except Exception as e:
        print(f"Erro ao dar baixa no recebimento: {e}")
        raise Exception(f"Erro ao dar baixa no recebimento: {str(e)}")


def listar_recebimentos(filtro_status=None, data_inicial=None, data_final=None):
    """
    Lista recebimentos com filtros opcionais
    
    Args:
        filtro_status (str, optional): Filtrar por status ('Pendente', 'Recebido', None para todos)
        data_inicial (date, optional): Filtrar por data de vencimento a partir desta data
        data_final (date, optional): Filtrar por data de vencimento até esta data
        
    Returns:
        list: Lista de tuplas com dados dos recebimentos
    """
    try:
        # Construir a consulta SQL de base
        query = """
        SELECT ID, CODIGO, CLIENTE, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
        FROM RECEBIMENTOS_CLIENTES
        WHERE 1=1
        """
        
        # Lista para armazenar os parâmetros
        params = []
        
        # Adicionar filtros conforme necessário
        if filtro_status:
            query += " AND STATUS = ?"
            params.append(filtro_status)
        
        if data_inicial:
            query += " AND VENCIMENTO >= ?"
            params.append(data_inicial)
        
        if data_final:
            query += " AND VENCIMENTO <= ?"
            params.append(data_final)
        
        # Adicionar ordenação
        query += " ORDER BY VENCIMENTO"
        
        # Executar a consulta
        return execute_query(query, tuple(params) if params else None)
    except Exception as e:
        print(f"Erro ao listar recebimentos: {e}")
        raise Exception(f"Erro ao listar recebimentos: {str(e)}")
    
def verificar_tabela_recebimentos_clientes():
    """Verifica se a tabela RECEBIMENTOS_CLIENTES existe e cria se necessário"""
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS
        WHERE RDB$RELATION_NAME = 'RECEBIMENTOS_CLIENTES'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, criar
        if result[0][0] == 0:
            query_create = """
            CREATE TABLE RECEBIMENTOS_CLIENTES (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(20),
                CLIENTE VARCHAR(100),
                CLIENTE_ID INTEGER,
                VENCIMENTO DATE,
                VALOR DECIMAL(15,2),
                DATA_RECEBIMENTO DATE,
                STATUS VARCHAR(20),
                VALOR_ORIGINAL DECIMAL(15,2)
            )
            """
            execute_query(query_create)
            print("Tabela RECEBIMENTOS_CLIENTES criada com sucesso!")
        else:
            # Verificar se a coluna VALOR_ORIGINAL existe
            query_check_column = """
            SELECT COUNT(*) FROM RDB$RELATION_FIELDS
            WHERE RDB$RELATION_NAME = 'RECEBIMENTOS_CLIENTES'
            AND RDB$FIELD_NAME = 'VALOR_ORIGINAL'
            """
            result = execute_query(query_check_column)
            
            # Se a coluna não existe, adicionar
            if result[0][0] == 0:
                query_add_column = """
                ALTER TABLE RECEBIMENTOS_CLIENTES
                ADD VALOR_ORIGINAL DECIMAL(15,2)
                """
                execute_query(query_add_column)
                
                # Atualizar valores existentes
                query_update = """
                UPDATE RECEBIMENTOS_CLIENTES
                SET VALOR_ORIGINAL = VALOR
                WHERE VALOR_ORIGINAL IS NULL
                """
                execute_query(query_update)
                
                print("Coluna VALOR_ORIGINAL adicionada com sucesso!")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        return False


def inserir_dados_exemplo_recebimentos():
    """
    Insere dados de exemplo na tabela de recebimentos para teste
    """
    try:
        # Verificar se já existem dados na tabela
        query_check = "SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES"
        result = execute_query(query_check)
        
        if result[0][0] > 0:
            print("Tabela RECEBIMENTOS_CLIENTES já possui dados. Pulando inserção de exemplos.")
            return
        
        # Dados de exemplo
        from datetime import datetime, timedelta
        hoje = datetime.now().date()
        
        # Datas de vencimento (em dias a partir de hoje)
        vencimentos = [1, 5, 10, 15, 30]
        
        dados = [
            ("001", "Empresa ABC Ltda", None, hoje + timedelta(days=vencimentos[0]), 5000.00),
            ("002", "João Silva", None, hoje + timedelta(days=vencimentos[1]), 1200.00),
            ("003", "Distribuidora XYZ", None, hoje + timedelta(days=vencimentos[2]), 3500.00),
            ("004", "Ana Souza", None, hoje + timedelta(days=vencimentos[3]), 750.00),
            ("005", "Mercado Central", None, hoje + timedelta(days=vencimentos[4]), 2100.00)
        ]
        
        # Inserir dados de exemplo
        query_insert = """
        INSERT INTO RECEBIMENTOS_CLIENTES (
            CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, STATUS
        ) VALUES (?, ?, ?, ?, ?, 'Pendente')
        """
        
        for dado in dados:
            execute_query(query_insert, dado)
            
        print("Dados de exemplo inseridos com sucesso na tabela RECEBIMENTOS_CLIENTES.")
    except Exception as e:
        print(f"Erro ao inserir dados de exemplo: {e}")
        # Não propagar o erro, apenas registrar

def listar_recebimentos_pendentes():
    """
    Lista todos os recebimentos pendentes
    
    Returns:
        list: Lista de tuplas com dados dos recebimentos pendentes
    """
    try:
        query = """
        SELECT ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, STATUS
        FROM RECEBIMENTOS_CLIENTES
        WHERE STATUS = 'Pendente'
        ORDER BY VENCIMENTO
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar recebimentos pendentes: {e}")
        raise Exception(f"Erro ao listar recebimentos pendentes: {str(e)}")

def listar_recebimentos_concluidos():
    """
    Lista todos os recebimentos já recebidos/baixados
    
    Returns:
        list: Lista de tuplas com dados dos recebimentos concluídos
    """
    try:
        query = """
        SELECT ID, CODIGO, CLIENTE, DATA_RECEBIMENTO, VALOR
        FROM RECEBIMENTOS_CLIENTES
        WHERE STATUS = 'Recebido'
        ORDER BY DATA_RECEBIMENTO DESC
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar recebimentos concluídos: {e}")
        raise Exception(f"Erro ao listar recebimentos concluídos: {str(e)}")

def buscar_recebimento_por_id(id_recebimento):
    """
    Busca um recebimento pelo ID
    
    Args:
        id_recebimento (int): ID do recebimento
        
    Returns:
        tuple: Dados do recebimento ou None se não encontrado
    """
    try:
        query = """
        SELECT * FROM RECEBIMENTOS_CLIENTES
        WHERE ID = ?
        """
        result = execute_query(query, (id_recebimento,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar recebimento: {e}")
        raise Exception(f"Erro ao buscar recebimento: {str(e)}")

def buscar_recebimentos_por_cliente(cliente):
    """
    Busca recebimentos por nome de cliente (busca parcial)
    
    Args:
        cliente (str): Nome do cliente (parcial)
        
    Returns:
        list: Lista de recebimentos encontrados
    """
    try:
        query = """
        SELECT ID, CODIGO, CLIENTE, VENCIMENTO, VALOR, STATUS
        FROM RECEBIMENTOS_CLIENTES
        WHERE UPPER(CLIENTE) LIKE UPPER(?)
        ORDER BY VENCIMENTO
        """
        return execute_query(query, (f"%{cliente}%",))
    except Exception as e:
        print(f"Erro ao buscar recebimentos por cliente: {e}")
        raise Exception(f"Erro ao buscar recebimentos por cliente: {str(e)}")

def filtrar_recebimentos(codigo=None, cliente=None, data_inicio=None, data_fim=None, status=None):
    """
    Filtra recebimentos com base em vários critérios
    
    Args:
        codigo (str, optional): Código do recebimento
        cliente (str, optional): Nome do cliente (busca parcial)
        data_inicio (date, optional): Data de vencimento inicial
        data_fim (date, optional): Data de vencimento final
        status (str, optional): Status do recebimento ('Pendente', 'Recebido')
        
    Returns:
        list: Lista de recebimentos filtrados
    """
    try:
        # Montar a query base
        query = """
        SELECT ID, CODIGO, CLIENTE, VENCIMENTO, VALOR, STATUS
        FROM RECEBIMENTOS_CLIENTES
        WHERE 1=1
        """
        
        # Lista para armazenar os parâmetros
        params = []
        
        # Adicionar filtros se fornecidos
        if codigo:
            query += " AND CODIGO = ?"
            params.append(codigo)
            
        if cliente:
            query += " AND UPPER(CLIENTE) LIKE UPPER(?)"
            params.append(f"%{cliente}%")
            
        if data_inicio:
            query += " AND VENCIMENTO >= ?"
            params.append(data_inicio)
            
        if data_fim:
            query += " AND VENCIMENTO <= ?"
            params.append(data_fim)
            
        if status:
            query += " AND STATUS = ?"
            params.append(status)
            
        # Ordenação
        query += " ORDER BY VENCIMENTO"
        
        return execute_query(query, tuple(params) if params else None)
    except Exception as e:
        print(f"Erro ao filtrar recebimentos: {e}")
        raise Exception(f"Erro ao filtrar recebimentos: {str(e)}")

def criar_recebimento(codigo, cliente, cliente_id=None, vencimento=None, valor=0, valor_original=None):
    """
    Cria um novo recebimento no banco de dados
    
    Args:
        codigo (str): Código do recebimento
        cliente (str): Nome do cliente
        cliente_id (int, optional): ID do cliente
        vencimento (date, optional): Data de vencimento
        valor (float): Valor do recebimento
        valor_original (float, optional): Valor original antes de pagamento parcial
    
    Returns:
        int: ID do recebimento criado
    """
    try:
        # Gerar ID explícito
        query_id = "SELECT COALESCE(MAX(ID), 0) + 1 FROM RECEBIMENTOS_CLIENTES"
        proximo_id = execute_query(query_id)[0][0]
        
        # Sanitizar e converter dados
        codigo = str(codigo).strip()[:20]
        cliente = str(cliente).strip()[:100]
        
        # Converter valor para float
        try:
            valor_float = float(valor)
        except (ValueError, TypeError):
            valor_float = 0
        
        # Converter data para formato do banco (se for string)
        if isinstance(vencimento, str):
            try:
                from datetime import datetime
                partes = vencimento.split('/')
                if len(partes) == 3:
                    vencimento = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                vencimento = None
        
        # Inserir o recebimento com ID explícito
        query = """
        INSERT INTO RECEBIMENTOS_CLIENTES (
            ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, STATUS
        ) VALUES (?, ?, ?, ?, ?, ?, 'Pendente')
        """
        
        params = (
            proximo_id, codigo, cliente, cliente_id, vencimento, valor_float
        )
        
        execute_query(query, params)
        
        return proximo_id
    except Exception as e:
        print(f"Erro ao criar recebimento: {e}")
        raise Exception(f"Erro ao criar recebimento: {str(e)}")


# Nova função para recriar a tabela com estrutura melhorada
def recriar_tabela_recebimentos():
    """Recria a tabela RECEBIMENTOS_CLIENTES com estrutura melhorada"""
    try:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Backup dos dados existentes
            cursor.execute("""
            CREATE TABLE RECEBIMENTOS_BACKUP AS 
            SELECT * FROM RECEBIMENTOS_CLIENTES
            """)
            
            # Dropar a tabela antiga
            cursor.execute("DROP TABLE RECEBIMENTOS_CLIENTES")
            
            # Criar nova tabela com restrições melhoradas
            cursor.execute("""
            CREATE TABLE RECEBIMENTOS_CLIENTES (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(40) NOT NULL,
                CLIENTE VARCHAR(100) NOT NULL,
                CLIENTE_ID INTEGER,
                VENCIMENTO DATE,
                VALOR DECIMAL(15,2) NOT NULL,
                DATA_RECEBIMENTO DATE,
                STATUS VARCHAR(20) DEFAULT 'Pendente',
                UNIQUE (CODIGO, STATUS)
            )
            """)
            
            # Recriar o gerador
            try:
                cursor.execute("DROP GENERATOR GEN_RECEBIMENTOS_ID")
            except:
                pass
            
            cursor.execute("CREATE GENERATOR GEN_RECEBIMENTOS_ID")
            
            # Recriar trigger
            cursor.execute("""
            CREATE TRIGGER RECEBIMENTOS_BI FOR RECEBIMENTOS_CLIENTES
            ACTIVE BEFORE INSERT POSITION 0
            AS
            BEGIN
                IF (NEW.ID IS NULL) THEN
                    NEW.ID = GEN_ID(GEN_RECEBIMENTOS_ID, 1);
            END
            """)
            
            # Restaurar dados
            cursor.execute("""
            INSERT INTO RECEBIMENTOS_CLIENTES 
            SELECT * FROM RECEBIMENTOS_BACKUP
            """)
            
            conn.commit()
            print("Tabela RECEBIMENTOS_CLIENTES recriada com sucesso!")
            
            # Remover backup
            cursor.execute("DROP TABLE RECEBIMENTOS_BACKUP")
            conn.commit()
            
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao recriar tabela: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"Erro ao recriar tabela: {e}")
        return False


# Função para limpar recebimentos antigos
def limpar_recebimentos_antigos():
    """Limpa recebimentos antigos já recebidos para liberar códigos"""
    try:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Contar quantos registros existem
            cursor.execute("SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES WHERE STATUS = 'Recebido'")
            count = cursor.fetchone()[0]
            
            if count > 0:
                # Mover para tabela de histórico
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS RECEBIMENTOS_HISTORICO (
                    ID INTEGER,
                    CODIGO VARCHAR(40),
                    CLIENTE VARCHAR(100),
                    CLIENTE_ID INTEGER,
                    VENCIMENTO DATE,
                    VALOR DECIMAL(15,2),
                    DATA_RECEBIMENTO DATE,
                    STATUS VARCHAR(20),
                    DATA_ARQUIVAMENTO TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                cursor.execute("""
                INSERT INTO RECEBIMENTOS_HISTORICO (ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS)
                SELECT ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS 
                FROM RECEBIMENTOS_CLIENTES 
                WHERE STATUS = 'Recebido'
                """)
                
                # Remover da tabela principal
                cursor.execute("DELETE FROM RECEBIMENTOS_CLIENTES WHERE STATUS = 'Recebido'")
                conn.commit()
                
                print(f"{count} recebimentos arquivados para o histórico!")
                return True
            
            return False
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao limpar recebimentos: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"Erro ao limpar recebimentos: {e}")
        return False


# Função para executar todas as correções necessárias
def executar_correcoes():
    """Executa correções necessárias na tabela de recebimentos"""
    try:
        # Verificar se a coluna VALOR_ORIGINAL existe
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se a coluna existe
            cursor.execute("""
            SELECT 1 FROM RDB$RELATION_FIELDS 
            WHERE RDB$RELATION_NAME = 'RECEBIMENTOS_CLIENTES' 
            AND RDB$FIELD_NAME = 'VALOR_ORIGINAL'
            """)
            
            if not cursor.fetchone():
                # A coluna não existe, vamos adicioná-la
                print("Adicionando coluna VALOR_ORIGINAL...")
                cursor.execute("ALTER TABLE RECEBIMENTOS_CLIENTES ADD VALOR_ORIGINAL DECIMAL(15,2)")
                
                # Inicializar com o valor atual
                cursor.execute("UPDATE RECEBIMENTOS_CLIENTES SET VALOR_ORIGINAL = VALOR")
                conn.commit()
                print("✓ Coluna VALOR_ORIGINAL adicionada e inicializada")
            else:
                print("✓ Coluna VALOR_ORIGINAL já existe")
                
        except Exception as e:
            print(f"Erro ao verificar coluna: {e}")
        finally:
            cursor.close()
            conn.close()
            
        print("Correções concluídas!")
        return True
    except Exception as e:
        print(f"Erro nas correções: {e}")
        return False

def dar_baixa_recebimento(id_recebimento, valor_pago, data_pagamento, criar_novo=True):
    """
    Dá baixa em um recebimento
    
    Args:
        id_recebimento (int): ID do recebimento
        valor_pago (float): Valor pago
        data_pagamento (date): Data do pagamento
        criar_novo (bool, optional): Se deve criar um novo registro para o pagamento. Defaults to True.
    """
    try:
        # Se deve criar um novo registro para o pagamento
        if criar_novo:
            # Gerar ID explícito para o registro de pagamento
            query_id = "SELECT COALESCE(MAX(ID), 0) + 1 FROM RECEBIMENTOS_CLIENTES"
            proximo_id = execute_query(query_id)[0][0]
            
            # Buscar dados do recebimento original
            recebimento = buscar_recebimento_por_id(id_recebimento)
            if not recebimento:
                raise Exception(f"Recebimento ID {id_recebimento} não encontrado")
            
            # Extrair dados
            codigo = recebimento[1]
            cliente = recebimento[2]
            cliente_id = recebimento[3]
            
            # Inserir registro de pagamento
            query = """
            INSERT INTO RECEBIMENTOS_CLIENTES (
                ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Recebido')
            """
            
            params = (
                proximo_id, codigo, cliente, cliente_id, data_pagamento, valor_pago, data_pagamento
            )
            
            execute_query(query, params)
            
            # Atualizar status do recebimento original
            query_update = """
            UPDATE RECEBIMENTOS_CLIENTES
            SET STATUS = 'Recebido'
            WHERE ID = ?
            """
            
            execute_query(query_update, (id_recebimento,))
        else:
            # Apenas registrar o pagamento sem criar novo registro
            # Inserir registro de pagamento
            query = """
            INSERT INTO RECEBIMENTOS_CLIENTES (
                CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            ) 
            SELECT CODIGO, CLIENTE, CLIENTE_ID, ?, ?, ?, 'Recebido'
            FROM RECEBIMENTOS_CLIENTES
            WHERE ID = ?
            """
            
            execute_query(query, (data_pagamento, valor_pago, data_pagamento, id_recebimento))
            
        return True
    except Exception as e:
        print(f"Erro ao dar baixa no recebimento: {e}")
        raise Exception(f"Erro ao dar baixa no recebimento: {str(e)}")


def atualizar_recebimento(id_recebimento, codigo=None, cliente=None, cliente_id=None, 
                        vencimento=None, valor=None, status=None):
    """
    Atualiza um recebimento existente
    
    Args:
        id_recebimento (int): ID do recebimento a ser atualizado
        codigo (str, optional): Novo código
        cliente (str, optional): Novo nome de cliente
        cliente_id (int, optional): Novo ID de cliente
        vencimento (date, optional): Nova data de vencimento
        valor (float, optional): Novo valor
        status (str, optional): Novo status
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se o recebimento existe
        recebimento = buscar_recebimento_por_id(id_recebimento)
        if not recebimento:
            raise Exception(f"Recebimento com ID {id_recebimento} não encontrado")
            
        # Campos para atualização
        campos = []
        params = []
        
        # Verificar cada campo a ser atualizado
        if codigo is not None:
            codigo = str(codigo).strip()[:20]
            # Verificar se este código já está em uso por outro recebimento
            if codigo != recebimento[1]:  # Código atual na posição 1
                outro_recebimento = buscar_recebimento_por_codigo(codigo)
                if outro_recebimento and outro_recebimento[0] != id_recebimento:
                    raise Exception(f"Código {codigo} já está em uso por outro recebimento")
            campos.append("CODIGO = ?")
            params.append(codigo)
            
        if cliente is not None:
            cliente = str(cliente).strip()[:100]
            campos.append("CLIENTE = ?")
            params.append(cliente)
            
        if cliente_id is not None:
            campos.append("CLIENTE_ID = ?")
            params.append(cliente_id)
            
        if vencimento is not None:
            campos.append("VENCIMENTO = ?")
            params.append(vencimento)
            
        if valor is not None:
            try:
                valor_float = float(valor)
                if valor_float <= 0:
                    raise Exception("O valor deve ser maior que zero")
                campos.append("VALOR = ?")
                params.append(valor_float)
            except (ValueError, TypeError):
                raise Exception("Valor inválido")
                
        if status is not None:
            if status not in ('Pendente', 'Recebido'):
                raise Exception("Status inválido. Use 'Pendente' ou 'Recebido'")
            campos.append("STATUS = ?")
            params.append(status)
            
        # Se não há campos para atualizar, retorna
        if not campos:
            return True
            
        # Montar query de atualização
        query = f"""
        UPDATE RECEBIMENTOS_CLIENTES SET
            {', '.join(campos)}
        WHERE ID = ?
        """
        
        # Adicionar o ID nos parâmetros
        params.append(id_recebimento)
        
        execute_query(query, tuple(params))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar recebimento: {e}")
        raise Exception(f"Erro ao atualizar recebimento: {str(e)}")

def excluir_recebimento(id_recebimento):
    """
    Exclui um recebimento do banco de dados e reorganiza os IDs se necessário
    
    Args:
        id_recebimento (int): ID do recebimento a ser excluído
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se o recebimento existe
        recebimento = buscar_recebimento_por_id(id_recebimento)
        if not recebimento:
            raise Exception(f"Recebimento com ID {id_recebimento} não encontrado")
            
        # Excluir recebimento
        query = """
        DELETE FROM RECEBIMENTOS_CLIENTES
        WHERE ID = ?
        """
        
        execute_query(query, (id_recebimento,))
        
        # Verificar se é necessário reorganizar os IDs (se houver poucos recebimentos restantes)
        query_count = """
        SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES
        """
        count_result = execute_query(query_count)
        
        # Se tiver menos de 5 recebimentos restantes, reorganizar os IDs
        if count_result[0][0] < 5:
            reorganizar_ids_recebimentos()
        
        return True
    except Exception as e:
        print(f"Erro ao excluir recebimento: {e}")
        raise Exception(f"Erro ao excluir recebimento: {str(e)}")

def reorganizar_ids_recebimentos():
    """
    Reorganiza os IDs da tabela RECEBIMENTOS_CLIENTES, eliminando lacunas
    e reiniciando a sequência do gerador
    """
    try:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Desativar as constraints temporariamente 
            # (isso pode variar dependendo da sua estrutura de banco)
            cursor.execute("UPDATE RDB$DATABASE SET RDB$CONSTRAINT_STATE = 0")
            
            # Criar tabela temporária com IDs sequenciais
            cursor.execute("""
            CREATE TABLE TEMP_RECEBIMENTOS AS
            SELECT ROW_NUMBER() OVER (ORDER BY ID) AS NEW_ID,
                CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            FROM RECEBIMENTOS_CLIENTES
            """)
            
            # Limpar a tabela original
            cursor.execute("DELETE FROM RECEBIMENTOS_CLIENTES")
            
            # Reinserir com IDs sequenciais
            cursor.execute("""
            INSERT INTO RECEBIMENTOS_CLIENTES (
                ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            )
            SELECT NEW_ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS
            FROM TEMP_RECEBIMENTOS
            """)
            
            # Reativar as constraints
            cursor.execute("UPDATE RDB$DATABASE SET RDB$CONSTRAINT_STATE = 1")
            
            # Remover tabela temporária
            cursor.execute("DROP TABLE TEMP_RECEBIMENTOS")
            
            # Resetar o gerador
            cursor.execute("SET GENERATOR GEN_RECEBIMENTOS_ID TO 0")
            
            # Configurar o gerador para o próximo ID
            cursor.execute("""
            SELECT COALESCE(MAX(ID), 0) FROM RECEBIMENTOS_CLIENTES
            """)
            max_id = cursor.fetchone()[0]
            cursor.execute(f"SET GENERATOR GEN_RECEBIMENTOS_ID TO {max_id}")
            
            conn.commit()
            print("IDs de recebimentos reorganizados com sucesso!")
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao reorganizar IDs: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        print(f"Erro ao reorganizar IDs: {e}")
        return False
    

def criar_recebimento(codigo, cliente, cliente_id=None, vencimento=None, valor=0, valor_original=None):
    """
    Cria um novo recebimento no banco de dados
    
    Args:
        codigo (str): Código do recebimento
        cliente (str): Nome do cliente
        cliente_id (int, optional): ID do cliente
        vencimento (date, optional): Data de vencimento
        valor (float): Valor do recebimento
        valor_original (float, optional): Valor original antes de pagamento parcial
    
    Returns:
        int: ID do recebimento criado
    """
    try:
        # Gerar ID explícito
        query_id = "SELECT COALESCE(MAX(ID), 0) + 1 FROM RECEBIMENTOS_CLIENTES"
        proximo_id = execute_query(query_id)[0][0]
        
        # Sanitizar e converter dados
        codigo = str(codigo).strip()[:20]
        cliente = str(cliente).strip()[:100]
        
        # Converter valor para float
        try:
            valor_float = float(valor)
        except (ValueError, TypeError):
            valor_float = 0
        
        # Se valor_original não foi fornecido, usar o valor atual
        if valor_original is None:
            valor_original = valor_float
        
        # Converter data para formato do banco (se for string)
        if isinstance(vencimento, str):
            try:
                from datetime import datetime
                partes = vencimento.split('/')
                if len(partes) == 3:
                    vencimento = datetime(int(partes[2]), int(partes[1]), int(partes[0]))
            except Exception as e:
                print(f"Erro ao converter data: {e}")
                vencimento = None
        
        # Inserir o recebimento com ID explícito
        query = """
        INSERT INTO RECEBIMENTOS_CLIENTES (
            ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, STATUS, VALOR_ORIGINAL
        ) VALUES (?, ?, ?, ?, ?, ?, 'Pendente', ?)
        """
        
        params = (
            proximo_id, codigo, cliente, cliente_id, vencimento, valor_float, valor_original
        )
        
        execute_query(query, params)
        
        return proximo_id
    except Exception as e:
        print(f"Erro ao criar recebimento: {e}")
        raise Exception(f"Erro ao criar recebimento: {str(e)}")

def atualizar_valor_original(recebimento_id, valor_original):
    """
    Atualiza o valor original de um recebimento existente
    
    Args:
        recebimento_id (int): ID do recebimento a ser atualizado
        valor_original (float): Valor original a ser salvo
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Garantir que o valor_original é do tipo correto
        try:
            valor_original = float(valor_original) if valor_original is not None else 0
        except (ValueError, TypeError):
            raise Exception(f"Valor original inválido: {valor_original}")
        
        # Atualizar o valor original
        query = """
        UPDATE RECEBIMENTOS_CLIENTES
        SET VALOR_ORIGINAL = ?
        WHERE ID = ?
        """
        
        execute_query(query, (valor_original, recebimento_id))
        
        print(f"Valor original atualizado com sucesso: ID={recebimento_id}, Valor Original={valor_original}")
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar valor original: {e}")
        raise Exception(f"Erro ao atualizar valor original: {str(e)}")

def buscar_recebimento_por_codigo_com_status(codigo):
    """
    Busca um recebimento pelo código e retorna também o status
    
    Args:
        codigo (str): Código do recebimento
        
    Returns:
        tuple: (ID, Código, Cliente, Status) ou None se não encontrado
    """
    try:
        query = """
        SELECT ID, CODIGO, CLIENTE, STATUS FROM RECEBIMENTOS_CLIENTES
        WHERE CODIGO = ?
        """
        result = execute_query(query, (codigo,))
        if result and len(result) > 0:
            return result[0]
        
        # Try with partial code match if exact match fails
        if not result or len(result) == 0:
            codigo_base = codigo.split('-')[0] if '-' in codigo else codigo
            query = """
            SELECT ID, CODIGO, CLIENTE, STATUS FROM RECEBIMENTOS_CLIENTES
            WHERE CODIGO LIKE ?
            """
            result = execute_query(query, (f"{codigo_base}%",))
            if result and len(result) > 0:
                return result[0]
                
        return None
    except Exception as e:
        print(f"Erro ao buscar recebimento por código: {e}")
        return None
    
def listar_clientes():
    """
    Lista todos os clientes cadastrados na tabela PESSOAS
    
    Returns:
        list: Lista de tuplas com (ID, NOME) dos clientes
    """
    try:
        query = """
        SELECT ID, NOME 
        FROM PESSOAS
        WHERE TIPO_PESSOA = 'Física' OR TIPO_PESSOA = 'Jurídica'
        ORDER BY NOME
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar clientes: {e}")
        # Tentar tabela alternativa se existir
        try:
            query = """
            SELECT ID, NOME_EMPRESA as NOME
            FROM EMPRESAS
            ORDER BY NOME_EMPRESA
            """
            return execute_query(query)
        except Exception as e2:
            print(f"Erro ao listar empresas: {e2}")
            return []
def buscar_recebimento_por_codigo(codigo):
    """Busca um recebimento pelo código"""
    try:
        # Construir a consulta SQL para busca exata
        query = """
        SELECT * FROM RECEBIMENTOS_CLIENTES
        WHERE CODIGO = ?
        """
        
        # Executar a consulta usando a função execute_query existente
        resultado = execute_query(query, (codigo,))
        
        # Se não encontrou e o código contém hífen (formato com parcelas)
        if (not resultado or len(resultado) == 0) and '-' in codigo:
            # Tentar buscar com o código base (antes do hífen)
            codigo_base = codigo.split('-')[0]
            query = """
            SELECT * FROM RECEBIMENTOS_CLIENTES
            WHERE CODIGO LIKE ?
            """
            resultado = execute_query(query, (f"{codigo_base}%",))
        
        # Retornar o primeiro resultado, se houver
        if resultado and len(resultado) > 0:
            return resultado[0]
        
        # Tente buscar pelo código parcial (para casos onde pode haver variações no formato)
        query = """
        SELECT * FROM RECEBIMENTOS_CLIENTES
        WHERE CODIGO LIKE ?
        """
        resultado = execute_query(query, (f"%{codigo}%",))
        
        if resultado and len(resultado) > 0:
            return resultado[0]
            
        return None
    except Exception as e:
        print(f"Erro ao buscar recebimento por código: {e}")
        return None
def excluir(self):
    """Ação do botão excluir"""
    selected_items = self.tabela.selectedItems()
    if not selected_items:
        self.mostrar_mensagem("Atenção", "Selecione um recebimento para excluir!")
        return
    
    # Obter a linha selecionada
    row = self.tabela.currentRow()
    codigo = self.tabela.item(row, 0).text()
    cliente = self.tabela.item(row, 1).text()
    
    # Mostrar mensagem de confirmação
    msgBox = QMessageBox()
    msgBox.setIcon(QMessageBox.Question)
    msgBox.setWindowTitle("Confirmação")
    msgBox.setText(f"Deseja realmente excluir o recebimento do cliente {cliente}?")
    msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msgBox.setStyleSheet("""
        QMessageBox { 
            background-color: white;
        }
        QLabel { 
            color: black;
            background-color: white;
        }
        QPushButton {
            background-color: #003b57;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 2px;
        }
    """)
    resposta = msgBox.exec_()
    
    if resposta == QMessageBox.Yes:
        try:
            # Primeiro, precisamos buscar todos os registros com este código base
            from base.banco import execute_query
            
            # Buscar registros pelo código (incluindo parcelas)
            query = """
            SELECT ID FROM RECEBIMENTOS_CLIENTES
            WHERE CODIGO LIKE ?
            """
            
            # Se o código tem formato com parcelas (ex: 2-1/2), pegamos apenas a parte base
            codigo_base = codigo
            if '-' in codigo:
                codigo_base = codigo.split('-')[0]
                
            # Buscar com wildcards para pegar todas as parcelas
            resultado = execute_query(query, (f"{codigo_base}%",))
            
            if resultado and len(resultado) > 0:
                # Para cada ID encontrado, excluir o registro
                for reg in resultado:
                    id_recebimento = reg[0]
                    from base.banco import excluir_recebimento
                    excluir_recebimento(id_recebimento)
                
                # Remover da tabela visual
                self.tabela.removeRow(row)
                self.mostrar_mensagem("Sucesso", "Recebimento excluído com sucesso!")
                print(f"Recebimento excluído: Código {codigo}, Cliente {cliente}")
            else:
                self.mostrar_mensagem("Erro", f"Não foi possível encontrar o recebimento com código {codigo}")
                
        except Exception as e:
            self.mostrar_mensagem("Erro", f"Erro ao excluir recebimento: {str(e)}")
def resetar_id_recebimentos():
    """
    Reseta a sequência de ID da tabela RECEBIMENTOS_CLIENTES para começar do 1
    
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Criar backup da tabela
        query_backup = """
        CREATE TABLE RECEBIMENTOS_CLIENTES_BACKUP AS 
        SELECT * FROM RECEBIMENTOS_CLIENTES
        """
        execute_query(query_backup)
        
        # Zerar o gerador
        query_reset = """
        SET GENERATOR GEN_RECEBIMENTOS_ID TO 0
        """
        execute_query(query_reset)
        
        print("Reset do ID de recebimentos concluído com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao resetar ID: {e}")
        raise Exception(f"Erro ao resetar ID: {str(e)}")
    
def verificar_e_corrigir_tabela_recebimentos():
    """Verifica e corrige a estrutura da tabela RECEBIMENTOS_CLIENTES, adicionando a coluna VALOR_ORIGINAL se necessário"""
    try:
        conn = None
        cursor = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Verificar se a coluna VALOR_ORIGINAL existe
            try:
                # Usar uma consulta compatível com Firebird para verificar se a coluna existe
                cursor.execute("""
                SELECT 1 FROM RDB$RELATION_FIELDS 
                WHERE RDB$RELATION_NAME = 'RECEBIMENTOS_CLIENTES' 
                AND RDB$FIELD_NAME = 'VALOR_ORIGINAL'
                """)
                
                resultado = cursor.fetchone()
                if resultado:
                    print("Coluna VALOR_ORIGINAL já existe.")
                else:
                    print("Adicionando coluna VALOR_ORIGINAL à tabela RECEBIMENTOS_CLIENTES...")
                    cursor.execute("ALTER TABLE RECEBIMENTOS_CLIENTES ADD VALOR_ORIGINAL DECIMAL(15,2)")
                    
                    # Preencher com o mesmo valor dos registros existentes
                    cursor.execute("UPDATE RECEBIMENTOS_CLIENTES SET VALOR_ORIGINAL = VALOR WHERE VALOR_ORIGINAL IS NULL")
                    conn.commit()
                    print("Coluna VALOR_ORIGINAL adicionada e inicializada com sucesso.")
            except Exception as e:
                print(f"Erro ao verificar coluna: {e}")
                
                try:
                    # Tentar adicionar a coluna de qualquer forma
                    cursor.execute("ALTER TABLE RECEBIMENTOS_CLIENTES ADD VALOR_ORIGINAL DECIMAL(15,2)")
                    
                    # Preencher com o mesmo valor dos registros existentes
                    cursor.execute("UPDATE RECEBIMENTOS_CLIENTES SET VALOR_ORIGINAL = VALOR")
                    conn.commit()
                    print("Coluna VALOR_ORIGINAL adicionada e inicializada com sucesso.")
                except Exception as e2:
                    print(f"Erro ao adicionar coluna: {e2}")
            
            return True
        except Exception as e:
            if conn:
                conn.rollback()
            print(f"Erro ao verificar/corrigir tabela: {e}")
            return False
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        print(f"Erro ao verificar/corrigir tabela: {e}")
        return False
    
def diagnosticar_recebimentos():
    """
    Função de diagnóstico para verificar o estado da tabela de recebimentos
    
    Returns:
        dict: Informações de diagnóstico
    """
    try:
        # Verificar total de registros
        query_count = """
        SELECT COUNT(*) FROM RECEBIMENTOS_CLIENTES
        """
        total_count = execute_query(query_count)[0][0]
        
        # Contar por status
        query_status = """
        SELECT STATUS, COUNT(*) FROM RECEBIMENTOS_CLIENTES
        GROUP BY STATUS
        """
        status_counts = execute_query(query_status)
        
        # Obter alguns registros para análise
        query_sample = """
        SELECT ID, CODIGO, CLIENTE, STATUS, VALOR 
        FROM RECEBIMENTOS_CLIENTES
        ORDER BY ID
        LIMIT 5
        """
        sample_records = execute_query(query_sample)
        
        # Montar resultado
        diagnostico = {
            "total_registros": total_count,
            "contagem_por_status": {status: count for status, count in status_counts},
            "registros_exemplo": sample_records
        }
        
        # Imprimir diagnóstico
        print("\n--- DIAGNÓSTICO DA TABELA RECEBIMENTOS_CLIENTES ---")
        print(f"Total de registros: {total_count}")
        print("Contagem por status:")
        for status, count in status_counts:
            print(f"  {status}: {count}")
        print("Registros exemplo:")
        for rec in sample_records:
            print(f"  ID={rec[0]}, Código={rec[1]}, Cliente={rec[2]}, Status={rec[3]}, Valor={rec[4]}")
        
        return diagnostico
    except Exception as e:
        print(f"Erro ao diagnosticar recebimentos: {e}")
        return {"erro": str(e)} 
# Adicionar à lista de inicialização no final do arquivo
if __name__ == "__main__":
    try:
        print(f"Iniciando configuração do banco de dados: {DB_PATH}")
        verificar_tabela_usuarios()
        verificar_tabela_empresas()
        verificar_tabela_pessoas()
        verificar_tabela_funcionarios()
        verificar_tabela_produtos()
        verificar_tabela_marcas()
        verificar_tabela_grupos()
        verificar_tabela_fornecedores()
        verificar_tabela_tipos_fornecedores()
        verificar_tabela_pedidos_venda() 
        verificar_tabela_recebimentos_clientes() 
        executar_correcoes()

        print("Banco de dados inicializado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {str(e)}")