"""
Módulo para gerenciar conexões com o banco de dados Firebird
"""
import os
import sys
import fdb  # Módulo para conexão com Firebird

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

def criar_usuario_padrao():
    """
    Cria um usuário padrão admin se não existir nenhum usuário
    
    Returns:
        bool: True se o usuário foi criado ou já existe
    """
    try:
        # Verificar se já existe algum usuário
        query_check = "SELECT COUNT(*) FROM USUARIOS"
        result = execute_query(query_check)
        
        # Se não existe nenhum usuário, criar um padrão
        if result[0][0] == 0:
            print("Nenhum usuário encontrado. Criando usuário padrão...")
            criar_usuario("admin", "admin", "MB SISTEMA")
            print("Usuário padrão criado com sucesso.")
            return True
        else:
            print(f"Já existem {result[0][0]} usuários cadastrados. Usuário padrão não será criado.")
        
        return True
    except Exception as e:
        print(f"Erro na criação do usuário padrão: {e}")
        raise Exception(f"Erro ao criar usuário padrão: {str(e)}")

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

if __name__ == "__main__":
    try:
        print(f"Iniciando configuração do banco de dados: {DB_PATH}")
        verificar_tabela_usuarios()
        verificar_tabela_empresas()
        verificar_tabela_pessoas()
        verificar_tabela_funcionarios()  # Adicionar esta linha
        criar_usuario_padrao()
        print("Banco de dados inicializado com sucesso!")
        
        # Listar usuários
        usuarios = listar_usuarios()
        print("\nUsuários cadastrados:")
        for usuario in usuarios:
            print(f"ID: {usuario[0]}, Usuário: {usuario[1]}, Empresa: {usuario[2]}")
        
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {str(e)}")

