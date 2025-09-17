# Arquivo: base/banco.py
# --- IMPORTS PADRÃO E DE OTIMIZAÇÃO ---
import os
import sys
import fdb
import functools
import threading
import time
import atexit
from datetime import date, datetime, timedelta
import glob
import hashlib
import base64
import random
import string
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
from PyQt5.QtWidgets import QMessageBox

print("Módulo 'banco.py' sendo carregado...")

# --- CONFIGURAÇÃO INICIAL E VARIÁVEIS GLOBAIS ---
SINCRONIZACAO_ATIVA = False
ULTIMA_SINCRONIZACAO = 0
INTERVALO_MIN_SYNC = 300  # 5 minutos

usuario_logado = {
    "id": None,
    "nome": None,
    "empresa": None
}

# --- FUNÇÕES DE CAMINHO E CONFIGURAÇÃO ---
def get_base_path():
    """Retorna o caminho base da aplicação, seja em modo dev ou compilado."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_db_path():
    """Determina o caminho do banco de dados MBDATA_NOVO.FDB de forma robusta."""
    base_dir = get_base_path()
    # Caminho principal (estrutura padrão)
    db_path = os.path.join(base_dir, "base", "banco", "MBDATA_NOVO.FDB")
    if os.path.isfile(db_path):
        return db_path

    # Caminho alternativo (caso a estrutura do executável seja diferente)
    alt_db_path = os.path.join(os.path.dirname(base_dir), "base", "banco", "MBDATA_NOVO.FDB")
    if os.path.isfile(alt_db_path):
        return alt_db_path
    
    # Se ainda não encontrou, assume o caminho principal e avisa
    print(f"AVISO: Banco de dados não encontrado. Tentando usar o caminho padrão: {db_path}")
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"Diretório criado: {db_dir}")
        except Exception as e:
            print(f"Erro ao criar diretório do banco: {e}")
    return db_path

# Configurações do banco (carregadas dinamicamente)
DB_PATH = get_db_path()
DB_USER = "SYSDBA"
DB_PASSWORD = "masterkey"
DB_HOST = "localhost"
DB_PORT = 3050

# --- OTIMIZAÇÃO: POOL DE CONEXÕES COM SQLAlchemy (O CORAÇÃO DA MELHORIA) ---
engine = None
DATABASE_URL = None
try:
    DATABASE_URL = f"firebird+fdb://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_PATH}?charset=UTF8"
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_recycle=3600,
        echo=False
    )
    with engine.connect() as conn: # Testa a conexão inicial
        print("✅ Pool de conexões com o banco de dados inicializado com sucesso.")
except Exception as e:
    print(f"❌ ERRO CRÍTICO: Não foi possível criar o pool de conexões. {e}")
    engine = None

# --- UTILITÁRIOS: GARANTIR EXISTÊNCIA DA TABELA CAIXA ---
# NO ARQUIVO base/banco.py, SUBSTITUA A FUNÇÃO ANTIGA POR ESTA:

def _ensure_caixa_table():
    """
    Verifica se a tabela CAIXA existe e a cria usando o método compatível
    de Generator e Trigger, caso não exista.
    """
    if not engine:
        print("⚠️  Engine não inicializada: não é possível verificar/criar tabela CAIXA.")
        return

    try:
        with engine.connect() as conn:
            # 1. Testa se a tabela CAIXA existe
            try:
                conn.execute(text("SELECT 1 FROM CAIXA WHERE 1=0"))
                print("Tabela CAIXA já existe — OK.")
                return # Se existe, não faz mais nada
            except Exception:
                print("Tabela CAIXA não encontrada — iniciando processo de criação.")

            # 2. Se não existe, cria a tabela, o generator e o trigger
            trans = conn.begin()
            try:
                # MUDANÇA 1: DDL sem a sintaxe 'IDENTITY'
                ddl_create_table = """
                CREATE TABLE CAIXA (
                    CODIGO INTEGER NOT NULL PRIMARY KEY,
                    ABERTURA TIMESTAMP,
                    FECHAMENTO TIMESTAMP,
                    USUARIO VARCHAR(50),
                    ESTACAO VARCHAR(50),
                    FUNDO_TROCO DECIMAL(10,2)
                );
                """
                conn.execute(text(ddl_create_table))
                print("-> Tabela CAIXA criada.")

                # MUDANÇA 2: Cria o GENERATOR (sequência) para o ID
                ddl_create_generator = "CREATE GENERATOR GEN_CAIXA_ID;"
                conn.execute(text(ddl_create_generator))
                print("-> Generator GEN_CAIXA_ID criado.")

                # MUDANÇA 3: Cria o TRIGGER para auto-incrementar o CODIGO
                ddl_create_trigger = """
                CREATE TRIGGER CAIXA_BI FOR CAIXA
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.CODIGO IS NULL) THEN
                        NEW.CODIGO = NEXT VALUE FOR GEN_CAIXA_ID;
                END
                """
                conn.execute(text(ddl_create_trigger))
                print("-> Trigger CAIXA_BI criado.")

                trans.commit()
                print("✅ Tabela CAIXA configurada com sucesso.")

            except Exception as e_create:
                print(f"❌ Erro durante a criação da estrutura da tabela CAIXA: {e_create}")
                trans.rollback()

    except Exception as e:
        print(f"❌ Erro crítico ao conectar ao banco para garantir a tabela CAIXA: {e}")

# --- OTIMIZAÇÃO: NOVA FUNÇÃO execute_query (ACEITA MAPPINGS E SEQUÊNCIAS) ---
def execute_query(query: str, params=None, commit=True):
    """
    Executa uma query no banco de dados usando o pool de conexões.
    Params pode ser:
      - um dict com parâmetros nomeados (':nome' no SQL)
      - uma tupla/lista de parâmetros posicionais
      - None
    Retorna lista de rows (list of sqlalchemy Row) ou [].
    """
    if not engine:
        raise ConnectionError("A conexão com o banco de dados não foi estabelecida.")

    with engine.connect() as connection:
        trans = connection.begin()
        try:
            # params pode ser dict ou sequência; text() aceita ambos
            result_proxy = connection.execute(text(query), params or {})
            result = result_proxy.fetchall() if result_proxy.returns_rows else []
            if commit:
                trans.commit()
            else:
                trans.rollback()
            return result
        except Exception as e:
            trans.rollback()
            print(f"❌ ERRO na execução da query:\nSQL: {query}\nParams: {params}\nErro: {e}")
            raise

# --- HELPERS PRÁTICOS PARA MÓDULO CAIXA ---
def fetch_caixas(codigo=None, usuario=None, inicio=None, fim=None, limit=1000):
    """
    Retorna lista de tuplas com (CODIGO, ABERTURA, FECHAMENTO, ESTACAO, USUARIO)
    Parâmetros:
      - codigo: inteiro ou string
      - usuario: string (busca LIKE)
      - inicio/fim: string 'YYYY-MM-DD' ou datetime
    """
    query = "SELECT CODIGO, ABERTURA, FECHAMENTO, ESTACAO, USUARIO FROM CAIXA WHERE 1=1"
    params = {}
    if codigo is not None and str(codigo).strip() != "":
        query += " AND CODIGO = :codigo"
        params["codigo"] = int(codigo)
    if usuario:
        query += " AND USUARIO LIKE :usuario"
        params["usuario"] = f"%{usuario}%"
    if inicio:
        query += " AND ABERTURA >= :inicio"
        params["inicio"] = inicio if isinstance(inicio, str) else inicio.strftime("%Y-%m-%d")
    if fim:
        query += " AND ABERTURA <= :fim"
        params["fim"] = fim if isinstance(fim, str) else fim.strftime("%Y-%m-%d")
    query += " ORDER BY ABERTURA DESC"
    if limit:
        # Firebird aceita FIRST
        query = query.replace("SELECT", f"SELECT FIRST {limit}", 1)
    return execute_query(query, params or {})

def abrir_caixa(usuario, estacao="ESTACAO_PADRAO", fundo_troco=0.0):
    """
    Insere um novo caixa e retorna o CODIGO (se possível).
    """
    # Firebird: usamos CURRENT_TIMESTAMP para ABERTURA
    query = """
    INSERT INTO CAIXA (ABERTURA, USUARIO, ESTACAO, FUNDO_TROCO)
    VALUES (CURRENT_TIMESTAMP, :usuario, :estacao, :fundo)
    """
    execute_query(query, {"usuario": usuario, "estacao": estacao, "fundo": float(fundo_troco)}, commit=True)
    # Tentamos retornar o último CODIGO inserido: em Firebird moderno poderia usar RETURNING,
    # mas para compatibilidade, fazemos um SELECT do último registro por ABERTURA.
    rows = execute_query("SELECT CODIGO FROM CAIXA ORDER BY ABERTURA DESC ROWS 1", {}, commit=False)
    return rows[0][0] if rows else None

def fechar_caixa(codigo):
    """
    Atualiza FECHAMENTO = CURRENT_TIMESTAMP para o CODIGO informado.
    Retorna True se atualizou algo.
    """
    query = "UPDATE CAIXA SET FECHAMENTO = CURRENT_TIMESTAMP WHERE CODIGO = :codigo"
    res = execute_query(query, {"codigo": int(codigo)}, commit=True)
    # execute_query retorna [] para não-SELECT; perguntamos quantas linhas afetadas:
    # Infelizmente fetchall não retorna affected_rows com text(). Então, para confirmar,
    # executamos um SELECT simples para verificar se FECHAMENTO foi preenchido.
    check = execute_query("SELECT FECHAMENTO FROM CAIXA WHERE CODIGO = :codigo", {"codigo": int(codigo)}, commit=False)
    return bool(check and check[0][0] is not None)

# --- FUNÇÃO DE DESLIGAMENTO ---
def desligar_banco():
    """Fecha o pool de conexões de forma segura."""
    global engine
    if engine:
        engine.dispose()
        print("🔌 Pool de conexões do banco de dados foi encerrado.")

# Garante que o pool seja fechado quando o programa terminar
atexit.register(desligar_banco)


# ==============================================================================
#  A PARTIR DAQUI VAMOS COLAR AS SUAS FUNÇÕES ANTIGAS, UMA POR UMA
# ==============================================================================

def iniciar_syncthing_se_necessario():
    """Inicia o Syncthing se ele não estiver em execução, usando o gerenciador singleton"""
    try:
        # Importar o gerenciador singleton
        from base.syncthing_manager import syncthing_manager
        
        # Iniciar o Syncthing através do gerenciador
        return syncthing_manager.iniciar_syncthing()
        
    except Exception as e:
        print(f"Erro ao tentar iniciar Syncthing: {e}")
        import traceback
        traceback.print_exc()
        return False

def configurar_syncthing():
    """Configura o comportamento do Syncthing para minimizar conflitos"""
    try:
        import os
        import json
        import xml.etree.ElementTree as ET
        from pathlib import Path
        
        # Encontrar o diretório de configuração do Syncthing
        home = str(Path.home())
        
        # Possíveis locais de configuração
        config_paths = [
            os.path.join(home, ".config", "syncthing"), # Linux
            os.path.join(home, "AppData", "Local", "Syncthing") # Windows
        ]
        
        config_path = None
        for path in config_paths:
            if os.path.exists(path):
                config_path = path
                break
        
        if not config_path:
            print("Diretório de configuração do Syncthing não encontrado")
            return False
        
        config_file = os.path.join(config_path, "config.xml")
        if not os.path.exists(config_file):
            print(f"Arquivo de configuração não encontrado: {config_file}")
            return False
        
        # Carregar e modificar configuração XML
        tree = ET.parse(config_file)
        root = tree.getroot()
        
        # Definir configurações para reduzir conflitos
        # Encontrar a seção de opções
        options = root.find("options")
        
        if options is not None:
            # Configurar para usar estratégia de resolução de conflitos mais conservadora
            conflict_elem = options.find("conflictResolutionStrategy")
            if conflict_elem is None:
                conflict_elem = ET.SubElement(options, "conflictResolutionStrategy")
            conflict_elem.text = "newest" # Usar o arquivo mais recente como vencedor
            
            # Salvar as alterações
            tree.write(config_file)
            print("Configuração do Syncthing atualizada")
            return True
        else:
            print("Seção de opções não encontrada no arquivo de configuração")
            return False
    
    except Exception as e:
        print(f"Erro ao configurar Syncthing: {e}")
        return False

def limpar_arquivos_conflito():
    """
    Remove arquivos temporários, de conflito e backups antigos da pasta do banco de dados
    """
    try:
        import os
        import time
        import glob
        from datetime import datetime, timedelta
        
        print("Verificando arquivos de conflito e temporários...")
        
        # Obter o diretório do banco de dados
        banco_dir = os.path.dirname(get_db_path())
        
        # Padrões de arquivos para remover
        padroes = [
            "*sync-conflict*",  # Arquivos de conflito do Syncthing
            "*.tmp",            # Arquivos temporários
            "*.bkp_*",          # Backups antigos com timestamp
            "*.old"             # Versões antigas
        ]
        
        # Data limite para manter backups (manter apenas últimos 3 dias)
        data_limite = datetime.now() - timedelta(days=3)
        
        total_removidos = 0
        for padrao in padroes:
            # Combinar o padrão com o diretório do banco
            caminho_padrao = os.path.join(banco_dir, padrao)
            
            # Encontrar arquivos correspondentes
            arquivos = glob.glob(caminho_padrao)
            
            for arquivo in arquivos:
                try:
                    # Verificar data de modificação
                    data_modificacao = datetime.fromtimestamp(os.path.getmtime(arquivo))
                    
                    # Para arquivos de backup, manter alguns recentes
                    if "_bkp" in arquivo and data_modificacao > data_limite:
                        continue
                    
                    # Verificar se o arquivo não está em uso
                    if not arquivo_esta_em_uso(arquivo):
                        print(f"Removendo arquivo: {os.path.basename(arquivo)}")
                        os.remove(arquivo)
                        total_removidos += 1
                except Exception as e:
                    print(f"Erro ao remover arquivo {arquivo}: {e}")
        
        print(f"Limpeza concluída. {total_removidos} arquivos removidos.")
        return total_removidos
    except Exception as e:
        print(f"Erro ao limpar arquivos de conflito: {e}")
        return 0

def arquivo_esta_em_uso(caminho_arquivo):
    """
    Verifica se um arquivo está em uso (bloqueado) por outro processo
    
    Args:
        caminho_arquivo (str): Caminho do arquivo a verificar
        
    Returns:
        bool: True se o arquivo estiver em uso, False caso contrário
    """
    try:
        # Tenta abrir o arquivo em modo exclusivo
        with open(caminho_arquivo, 'a+b') as f:
            # Se conseguir obter um lock exclusivo, o arquivo não está em uso
            return False
    except IOError:
        # Se ocorrer erro, o arquivo está em uso
        return True
    except Exception:
        # Para qualquer outro erro, assumir que está em uso por segurança
        return True
    
def controlar_sincronizacao():
    """Controla o processo de sincronização do banco principal"""
    global SINCRONIZACAO_ATIVA, ULTIMA_SINCRONIZACAO
    
    # Verificar condições para sincronização
    agora = time.time()
    tempo_passado = agora - ULTIMA_SINCRONIZACAO
    
    # Se sincronização já estiver ativa ou tempo mínimo não passou
    if SINCRONIZACAO_ATIVA or tempo_passado < INTERVALO_MIN_SYNC:
        return False
    
    try:
        # Marcar como ativa
        SINCRONIZACAO_ATIVA = True
        
        # Verificar conectividade
        if not verificar_conectividade():
            print("Sem conectividade para sincronização")
            SINCRONIZACAO_ATIVA = False
            return False
        
        # Aguardar banco ficar livre (tentar por até 10 segundos)
        tentativas = 10
        while banco_em_uso() and tentativas > 0:
            time.sleep(1)
            tentativas -= 1
        
        if banco_em_uso():
            print("Banco em uso, sincronização adiada")
            SINCRONIZACAO_ATIVA = False
            return False
        
        # Limpar arquivos de conflito ANTES da sincronização
        try:
            limpar_arquivos_conflito()
        except Exception as e:
            print(f"Aviso: Erro ao limpar arquivos de conflito: {e}")
        
        # Banco livre, pode sincronizar
        print(f"Sincronizando banco principal em {time.strftime('%H:%M:%S')}")
        
        # O Syncthing fará a sincronização por conta própria
        # Vamos apenas garantir que o arquivo seja "tocado" para ser detectado
        caminho_banco = get_db_path()
        os.utime(caminho_banco, None)
        
        # Atualizar timestamp da última sincronização
        ULTIMA_SINCRONIZACAO = time.time()
        
        print("Sincronização do banco completa!")
        return True
        
    except Exception as e:
        print(f"Erro durante sincronização do banco: {e}")
        return False
    finally:
        # Garantir que o status seja atualizado
        SINCRONIZACAO_ATIVA = False

# Função para executar em uma thread separada
def monitor_sincronizacao():
    """Thread que monitora e executa sincronizações periódicas"""
    while True:
        # Verificar a cada 2 minutos
        time.sleep(120)
        if not banco_em_uso():
            controlar_sincronizacao()

def sincronizar_ao_encerrar():
    """Realiza sincronização ao encerrar o programa"""
    if verificar_conectividade() and not banco_em_uso():
        print("Sincronizando banco antes de encerrar...")
        # O Syncthing detectará as alterações e sincronizará
        caminho_banco = get_db_path()
        try:
            # Tocar o arquivo para garantir que o Syncthing o detecte
            os.utime(caminho_banco, None)
            time.sleep(2)  # Pequena pausa para o Syncthing iniciar o processo
        except Exception as e:
            print(f"Erro na sincronização final: {e}")

def obter_caminho_banco_backup():
    """Retorna o caminho para o arquivo de backup na pasta banco"""
    import os
    # Usamos a mesma pasta base, mas com nome de arquivo diferente para backup
    caminho_base = get_base_path()
    caminho_pasta_banco = os.path.join(caminho_base, "base", "banco")
    
    # Garantir que a pasta base/banco existe
    if not os.path.exists(caminho_pasta_banco):
        os.makedirs(caminho_pasta_banco, exist_ok=True)
    
    return os.path.join(caminho_pasta_banco, "MBDATA_NOVO_bkp")

def criar_backup_banco():
    """Cria um backup do banco local"""
    import shutil
    import time
    
    try:
        origem = get_db_path()  # Banco original
        destino = obter_caminho_banco_backup()  # Arquivo de backup
        
        print(f"Criando backup: {origem} -> {destino}")
        
        # Aguardar um pouco para garantir que todas as transações estejam completas
        time.sleep(1)
        
        # Verificar se o banco está sendo usado
        try:
            with open(origem, 'rb') as f_origem:
                # Criar backup
                shutil.copy2(origem, destino)
            print("Backup criado com sucesso!")
            return True
        except PermissionError:
            print("Não foi possível criar backup - banco em uso")
            return False
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return False

def restaurar_backup():
    """Restaura o banco a partir do backup quando necessário"""
    import shutil
    import os
    
    try:
        origem = obter_caminho_banco_backup()  # Arquivo de backup
        destino = get_db_path()  # Banco original
        
        # Verificar se o backup existe
        if not os.path.exists(origem):
            print("Arquivo de backup não encontrado")
            return False
        
        print(f"Restaurando backup: {origem} -> {destino}")
        
        # Verificar se é mais recente que o original
        backup_time = os.path.getmtime(origem)
        original_time = os.path.getmtime(destino) if os.path.exists(destino) else 0
        
        if backup_time <= original_time:
            print("Backup é mais antigo que o banco atual - ignorando")
            return False
        
        # Fazer backup do banco atual antes de substituir (por segurança)
        if os.path.exists(destino):
            shutil.copy2(destino, destino + ".old")
        
        # Restaurar o backup
        shutil.copy2(origem, destino)
        print("Backup restaurado com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao restaurar backup: {e}")
        return False

def sincronizar_banco(force=False):
    """Verifica e sincroniza o banco de dados"""
    online = verificar_conectividade()
    
    # Se online, criar backup para sincronização
    if online or force:
        return criar_backup_banco()
    
    return False

def obter_estacao_atual():
    """
    Obtém o nome da estação atual (computador)
    
    Returns:
        str: Nome da estação
    """
    try:
        import socket   
        return socket.gethostname()
    except Exception as e:
        print(f"Erro ao obter nome da estação: {e}")
        return "Estação Desconhecida"
    
def get_base_path():
    if getattr(sys, 'frozen', False):
        # Executando como executable
        base_dir = os.path.dirname(sys.executable)
    else:
        # Executando em desenvolvimento
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return base_dir

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
            os.path.join(base_dir, "base", "banco", "MBDATA_NOVO.FDB"),
            # Caminho relativo ao executável (pasta pai)
            os.path.join(os.path.dirname(base_dir), "base", "banco", "MBDATA_NOVO.FDB"),
            # Caminho absoluto fixo (caso seja uma instalação específica)
            r"C:\MBSistema\base\banco\MBDATA_NOVO.FDB",
        ]
    else:
        # Se estiver executando em modo de desenvolvimento
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_paths = [
            # Caminho relativo ao script atual
            os.path.join(base_dir, "base", "banco", "MBDATA_NOVO.FDB"),
            # Caminho alternativo (um nível acima)
            os.path.join(os.path.dirname(base_dir), "base", "banco", "MBDATA_NOVO.FDB"),
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

def execute_query(query, params=None, commit=True, verificar_sync=True):
    """
    Executa uma query no banco de dados com suporte a sincronização
    """
    conn = None
    cursor = None
    try:
        conn = get_connection(verificar_sync=verificar_sync)
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

def verificar_conectividade():
    """Verifica se há conexão com a internet"""
    try:
        import socket
        socket.create_connection(("www.google.com", 80), timeout=3)
        return True
    except OSError:
        return False
def banco_em_uso():
    """Verifica se o banco de dados está em uso no momento"""
    try:
        # Tenta abrir o arquivo do banco para verificar se está bloqueado
        caminho_banco = get_db_path()
        with open(caminho_banco, 'rb') as f:
            # Tenta apenas ler o começo do arquivo para verificar acesso
            f.read(10)
            return False  # Se conseguir abrir, o banco não está em uso exclusivo
    except (IOError, PermissionError):
        return True  # Erro ao abrir, indica que o banco está em uso
    except Exception as e:
        print(f"Erro ao verificar uso do banco: {e}")
        return True  # Em caso de dúvida, considerar como em uso

# Modifique a função get_connection para verificar sincronização
def get_connection(verificar_sync=True):
    """
    Retorna uma conexão com o banco de dados Firebird
    E realiza sincronização se necessário
    """
    try:
        # Verificar se há um backup mais recente para restaurar
        if verificar_sync and verificar_conectividade():
            restaurar_backup()
        
        # Obter caminho do banco atual
        db_path = get_db_path()
        print(f"Tentando conectar ao banco de dados: {db_path}")
        
        # Conectar ao banco
        conn = fdb.connect(
            host=DB_HOST,
            database=db_path,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT,
            charset='UTF8'
        )
        
        # Após a conexão bem-sucedida, verificar sincronização
        if verificar_sync:
            # Executar em background para não bloquear
            import threading
            threading.Thread(target=sincronizar_banco).start()
            
        return conn
    except Exception as e:
        print(f"Erro de conexão: {e}")
        raise Exception(f"Erro ao conectar ao banco de dados: {str(e)}")

#LOGIN 
def validar_login(usuario, senha, empresa):
    """
    Valida o login do usuário e verifica se está bloqueado
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha do usuário
        empresa (str): Nome da empresa
        
    Returns:
        bool: True se o login for válido e não estiver bloqueado, False caso contrário
    """
    try:
        # Primeiro verificar se o usuário está bloqueado
        bloqueado, motivo = verificar_usuario_bloqueado(usuario, empresa)
        if bloqueado:
            # Adicionar o motivo ao log para depuração
            print(f"Login negado para {usuario}: {motivo}")
            # Criar exceção com a mensagem de bloqueio para ser exibida ao usuário
            raise Exception(motivo)
        
        # Verificação normal de credenciais
        query = """
        SELECT ID, USUARIO, EMPRESA FROM USUARIOS 
        WHERE USUARIO = ? AND SENHA = ? AND EMPRESA = ?
        """
        result = execute_query(query, (usuario, senha, empresa))
        
        # Se encontrou pelo menos um usuário com essas credenciais
        if result and len(result) > 0:
            # Armazenar informações do usuário logado
            global usuario_logado
            usuario_logado["id"] = result[0][0]
            usuario_logado["nome"] = result[0][1]
            usuario_logado["empresa"] = result[0][2]
            return True
        return False
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

def bloquear_usuario(id_usuario, motivo=None):
    """
    Bloqueia um usuário e todos os usuários vinculados a ele
    
    Args:
        id_usuario (int): ID do usuário a ser bloqueado
        motivo (str, optional): Motivo do bloqueio
        
    Returns:
        bool: True se o bloqueio foi bem-sucedido
    """
    try:
        from datetime import date
        
        # Bloquear o usuário principal
        query = """
        UPDATE USUARIOS
        SET BLOQUEADO = 'S', 
            DATA_BLOQUEIO = ?,
            MOTIVO_BLOQUEIO = ?
        WHERE ID = ?
        """
        
        execute_query(query, (date.today(), motivo, id_usuario))
        
        # Bloquear todos os usuários vinculados
        query_vinculados = """
        UPDATE USUARIOS
        SET BLOQUEADO = 'S', 
            DATA_BLOQUEIO = ?,
            MOTIVO_BLOQUEIO = 'Conta principal bloqueada'
        WHERE USUARIO_MASTER = ?
        """
        
        execute_query(query_vinculados, (date.today(), id_usuario))
        
        return True
    except Exception as e:
        print(f"Erro ao bloquear usuário: {e}")
        raise Exception(f"Erro ao bloquear usuário: {str(e)}")

def desbloquear_usuario(id_usuario):
    """
    Desbloqueia um usuário e todos os usuários vinculados a ele
    
    Args:
        id_usuario (int): ID do usuário a ser desbloqueado
        
    Returns:
        bool: True se o desbloqueio foi bem-sucedido
    """
    try:
        # Desbloquear o usuário principal
        query = """
        UPDATE USUARIOS
        SET BLOQUEADO = 'N', 
            DATA_BLOQUEIO = NULL,
            MOTIVO_BLOQUEIO = NULL
        WHERE ID = ?
        """
        
        execute_query(query, (id_usuario,))
        
        # Desbloquear todos os usuários vinculados
        query_vinculados = """
        UPDATE USUARIOS
        SET BLOQUEADO = 'N', 
            DATA_BLOQUEIO = NULL,
            MOTIVO_BLOQUEIO = NULL
        WHERE USUARIO_MASTER = ?
        """
        
        execute_query(query_vinculados, (id_usuario,))
        
        return True
    except Exception as e:
        print(f"Erro ao desbloquear usuário: {e}")
        raise Exception(f"Erro ao desbloquear usuário: {str(e)}")

def verificar_usuario_bloqueado(usuario, empresa=None):
    """
    Verifica se um usuário está bloqueado ou com pagamento pendente
    
    Args:
        usuario (str): Nome do usuário
        empresa (str, optional): Nome da empresa
        
    Returns:
        tuple: (bool, str) - (está_bloqueado, motivo)
    """
    try:
        where_clause = "WHERE USUARIO = ?"
        params = [usuario]
        
        if empresa:
            where_clause += " AND EMPRESA = ?"
            params.append(empresa)
        
        query = f"""
        SELECT BLOQUEADO, MOTIVO_BLOQUEIO, DATA_EXPIRACAO, USUARIO_MASTER
        FROM USUARIOS
        {where_clause}
        """
        
        result = execute_query(query, tuple(params))
        
        if not result or len(result) == 0:
            return False, ""
            
        bloqueado, motivo, data_expiracao, usuario_master = result[0]
        
        # Verificar se o usuário está explicitamente bloqueado
        if bloqueado and bloqueado.upper() == 'S':
            return True, motivo or "Usuário bloqueado"
            
        # Verificar se a data de expiração foi atingida
        if data_expiracao:
            from datetime import date
            hoje = date.today()
            if hoje > data_expiracao:
                return True, "Mensalidade vencida. Por favor, entre em contato com o suporte."
                
        # Se for um usuário vinculado a um master, verificar se o master está bloqueado
        if usuario_master:
            # Buscar o usuário master
            query_master = """
            SELECT BLOQUEADO, MOTIVO_BLOQUEIO
            FROM USUARIOS
            WHERE ID = ?
            """
            
            result_master = execute_query(query_master, (usuario_master,))
            
            if result_master and len(result_master) > 0:
                bloqueado_master, motivo_master = result_master[0]
                
                if bloqueado_master and bloqueado_master.upper() == 'S':
                    return True, motivo_master or "Conta principal bloqueada"
        
        return False, ""
    except Exception as e:
        print(f"Erro ao verificar bloqueio: {e}")
        return False, ""

def atualizar_data_expiracao(id_usuario, nova_data):
    """
    Atualiza a data de expiração para um usuário e seus vinculados
    
    Args:
        id_usuario (int): ID do usuário
        nova_data (date): Nova data de expiração
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Atualizar usuário principal
        query = """
        UPDATE USUARIOS
        SET DATA_EXPIRACAO = ?
        WHERE ID = ?
        """
        
        execute_query(query, (nova_data, id_usuario))
        
        # Atualizar usuários vinculados
        query_vinculados = """
        UPDATE USUARIOS
        SET DATA_EXPIRACAO = ?
        WHERE USUARIO_MASTER = ?
        """
        
        execute_query(query_vinculados, (nova_data, id_usuario))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar data de expiração: {e}")
        raise Exception(f"Erro ao atualizar data de expiração: {str(e)}")

def verificar_tabela_licencas():
    """Verifica se a tabela de licenças existe e a cria se não existir"""
    try:
        query = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'LICENCAS'
        """
        result = execute_query(query)
        
        if result[0][0] == 0:
            query_create = """
            CREATE TABLE LICENCAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                USUARIO_ID INTEGER NOT NULL,
                CODIGO VARCHAR(50) NOT NULL,
                DATA_GERACAO DATE NOT NULL,
                DATA_EXPIRACAO DATE NOT NULL,
                ATIVO CHAR(1) DEFAULT 'S',
                FOREIGN KEY (USUARIO_ID) REFERENCES USUARIOS(ID)
            )
            """
            execute_query(query_create)
            execute_query("CREATE SEQUENCE GEN_LICENCAS_ID")
            
            trigger_query = """
            CREATE TRIGGER LICENCAS_BI FOR LICENCAS
            ACTIVE BEFORE INSERT POSITION 0
            AS
            BEGIN
                IF (NEW.ID IS NULL) THEN
                    NEW.ID = NEXT VALUE FOR GEN_LICENCAS_ID;
            END
            """
            execute_query(trigger_query)
            
            print("Tabela LICENCAS criada com sucesso.")
    except Exception as e:
        print(f"Erro ao verificar/criar tabela LICENCAS: {e}")
        raise

def gerar_codigo_licenca(usuario_id, data_expiracao):
    """Gera um código de licença criptografado"""
    # Criar string com os dados
    expiracao_str = data_expiracao.strftime('%Y%m%d')
    dados = f"{usuario_id}-{expiracao_str}-{int(time.time())}"
    
    # Adicionar salt aleatório
    salt = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    dados_com_salt = f"{dados}-{salt}"
    
    # Criar hash
    hash_obj = hashlib.sha256(dados_com_salt.encode())
    hash_bytes = hash_obj.digest()
    
    # Converter para base64 e formatar
    codigo_base64 = base64.b64encode(hash_bytes).decode()
    codigo_limpo = codigo_base64.replace('/', '_').replace('+', '-').replace('=', '')
    
    # Código final no formato: ID-HASH
    codigo_final = f"{usuario_id:04d}-{codigo_limpo[:16]}"
    
    return codigo_final

def salvar_codigo_licenca(usuario_id, codigo, data_geracao, data_expiracao):
    """Salva um código de licença no banco"""
    try:
        # Inativar códigos anteriores
        execute_query("UPDATE LICENCAS SET ATIVO = 'N' WHERE USUARIO_ID = ? AND ATIVO = 'S'", 
                     (usuario_id,))
        
        # Inserir novo código
        execute_query("""INSERT INTO LICENCAS 
                       (USUARIO_ID, CODIGO, DATA_GERACAO, DATA_EXPIRACAO, ATIVO)
                       VALUES (?, ?, ?, ?, 'S')""",
                     (usuario_id, codigo, data_geracao.strftime('%Y-%m-%d'), 
                      data_expiracao.strftime('%Y-%m-%d')))
        return True
    except Exception as e:
        print(f"Erro ao salvar código: {e}")
        return False

def validar_codigo_licenca(codigo, usuario_id):
    """Verifica se um código é válido"""
    try:
        # Verificar formato do código
        partes = codigo.split('-')
        if len(partes) < 2 or int(partes[0]) != usuario_id:
            return False
        
        # Consultar banco
        query = """SELECT COUNT(*) FROM LICENCAS 
                  WHERE USUARIO_ID = ? AND CODIGO = ? AND ATIVO = 'S' 
                  AND DATA_EXPIRACAO >= CURRENT_DATE"""
        result = execute_query(query, (usuario_id, codigo))
        
        return result[0][0] > 0
    except Exception:
        return False

def obter_id_usuario(usuario, empresa):
    """Obtém o ID do usuário com base no nome e empresa"""
    try:
        query = "SELECT ID FROM USUARIOS WHERE USUARIO = ? AND EMPRESA = ?"
        result = execute_query(query, (usuario, empresa))
        if result and len(result) > 0:
            return result[0][0]
        return None
    except Exception as e:
        print(f"Erro ao obter ID do usuário: {e}")
        return None

def verificar_necessidade_codigo_licenca(usuario_id):
    """Verifica se o usuário precisa informar um código de licença"""
    try:
        # Verificar se é um usuário master
        query = """
        SELECT DATA_EXPIRACAO, USUARIO_MASTER 
        FROM USUARIOS 
        WHERE ID = ?
        """
        result = execute_query(query, (usuario_id,))
        
        if not result or len(result) == 0:
            return False
            
        data_expiracao, usuario_master = result[0]
        
        # Se for usuário vinculado, verificar usuario master
        if usuario_master:
            query_master = "SELECT DATA_EXPIRACAO FROM USUARIOS WHERE ID = ?"
            result_master = execute_query(query_master, (usuario_master,))
            
            if result_master and len(result_master) > 0:
                data_expiracao_master = result_master[0][0]
                
                # Se o master estiver vencido, precisa de código
                if data_expiracao_master and date.today() > data_expiracao_master:
                    return True
            
            # Se não encontrou master ou não tem data vencida, verifica só este usuário
        
        # Verificar se a data de expiração está vencida
        if data_expiracao and date.today() > data_expiracao:
            return True
            
        # Verificar se está próximo de vencer (7 dias ou menos)
        dias_para_vencer = (data_expiracao - date.today()).days
        if dias_para_vencer <= 7:
            # Opcional: mostrar aviso mas não exigir código ainda
            pass
            
        return False
    except Exception as e:
        print(f"Erro ao verificar necessidade de código: {e}")
        return False

def atualizar_data_expiracao_por_codigo(codigo, usuario_id):
    """Atualiza a data de expiração do usuário com base no código de licença"""
    try:
        # Buscar dados do código
        query = """
        SELECT DATA_EXPIRACAO 
        FROM LICENCAS 
        WHERE CODIGO = ? AND USUARIO_ID = ? AND ATIVO = 'S'
        """
        result = execute_query(query, (codigo, usuario_id))
        
        if result and len(result) > 0:
            nova_data = result[0][0]
            
            # Atualizar data de expiração do usuário
            update_query = "UPDATE USUARIOS SET DATA_EXPIRACAO = ? WHERE ID = ?"
            execute_query(update_query, (nova_data, usuario_id))
            
            return True
        return False
    except Exception as e:
        print(f"Erro ao atualizar data de expiração: {e}")
        return False

def verificar_usuario_bloqueado(usuario, empresa):
    """Verifica se o usuário está bloqueado e retorna o motivo"""
    try:
        # Verificar bloqueio direto
        query = """
        SELECT BLOQUEADO, MOTIVO_BLOQUEIO, USUARIO_MASTER 
        FROM USUARIOS 
        WHERE USUARIO = ? AND EMPRESA = ?
        """
        result = execute_query(query, (usuario, empresa))
        
        if not result or len(result) == 0:
            return False, ""
            
        bloqueado, motivo, usuario_master = result[0]
        
        # Verificar se está bloqueado diretamente
        if bloqueado and bloqueado.upper() == 'S':
            if not motivo:
                motivo = "Usuário bloqueado. Entre em contato com o suporte."
            return True, motivo
        
        # Se for um usuário vinculado, verificar se o master está bloqueado
        if usuario_master:
            query_master = """
            SELECT BLOQUEADO, MOTIVO_BLOQUEIO 
            FROM USUARIOS 
            WHERE ID = ?
            """
            result_master = execute_query(query_master, (usuario_master,))
            
            if result_master and len(result_master) > 0:
                bloqueado_master, motivo_master = result_master[0]
                
                if bloqueado_master and bloqueado_master.upper() == 'S':
                    if not motivo_master:
                        motivo_master = "Conta principal bloqueada. Entre em contato com o suporte."
                    return True, motivo_master
        
        return False, ""
    except Exception as e:
        print(f"Erro ao verificar bloqueio: {e}")
        return False, "Erro ao verificar status do usuário"
    

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
    
@functools.lru_cache(maxsize=512)
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

def buscar_empresas_por_filtro(codigo: str, nome: str, documento: str):
    """
    Busca empresas no banco de dados com base em filtros dinâmicos.
    
    Returns:
        list: Lista de tuplas com (ID, NOME_EMPRESA, DOCUMENTO)
    """
    try:
        query = "SELECT ID, NOME_EMPRESA, DOCUMENTO FROM EMPRESAS WHERE 1=1"
        params = []
        
        if codigo:
            query += " AND ID = ?"
            params.append(int(codigo))
        if nome:
            query += " AND UPPER(NOME_EMPRESA) LIKE UPPER(?)"
            params.append(f"%{nome}%")
        if documento:
            doc_limpo = ''.join(filter(str.isdigit, documento))
            if doc_limpo:
                query += " AND DOCUMENTO LIKE ?"
                params.append(f"%{doc_limpo}%")
        
        query += " ORDER BY ID"
        return execute_query(query, tuple(params))
    except Exception as e:
        print(f"Erro ao buscar empresas por filtro: {e}")
        return []

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
@functools.lru_cache(maxsize=512)
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
@functools.lru_cache(maxsize=512)
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
@functools.lru_cache(maxsize=512)
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

@functools.lru_cache(maxsize=128)
def buscar_fornecedor_por_id(id_fornecedor):
    """Busca um fornecedor pelo seu ID (PK)."""
    # A sua lógica de busca continua a mesma aqui dentro
    try:
        query = "SELECT * FROM FORNECEDORES WHERE ID = ?"
        resultado = execute_query(query, (id_fornecedor,))
        return resultado[0] if resultado else None
    except Exception as e:
        print(f"Erro ao buscar fornecedor por ID {id_fornecedor}: {e}")
        return None

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
@functools.lru_cache(maxsize=512)
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
    
@functools.lru_cache(maxsize=512)
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
@functools.lru_cache(maxsize=512)
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
    Filtra recebimentos com base nos critérios especificados
    
    Args:
        codigo (str, optional): Filtra por código. Defaults to None.
        cliente (str, optional): Filtra por cliente. Defaults to None.
        data_inicio (date, optional): Data de início para filtrar. Defaults to None.
        data_fim (date, optional): Data final para filtrar. Defaults to None.
        status (str, optional): Status do recebimento. Defaults to None.
        
    Returns:
        list: Lista de tuplas com os recebimentos filtrados
    """
    try:
        # Começar com uma consulta base
        query = """
        SELECT ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS, VALOR_ORIGINAL
        FROM RECEBIMENTOS_CLIENTES 
        WHERE 1=1
        """
        
        params = []
        
        # Adicionar condições conforme os filtros fornecidos
        if codigo:
            # Para código, usamos busca por prefixo ou código exato
            codigo_base = codigo.split('-')[0] if '-' in codigo else codigo
            query += " AND (CODIGO LIKE ? OR CODIGO = ?)"
            params.extend([f"{codigo_base}%", codigo])
        
        if cliente:
            # Para cliente, usamos busca parcial com LIKE e case-insensitive
            query += " AND UPPER(TRIM(CLIENTE)) LIKE UPPER(?)"
            params.append(f"%{cliente}%")
        
        if data_inicio:
            # Converter para string se for um objeto date
            if hasattr(data_inicio, 'strftime'):
                data_inicio_str = data_inicio.strftime('%Y-%m-%d')
            else:
                data_inicio_str = data_inicio
            
            query += " AND VENCIMENTO >= ?"
            params.append(data_inicio_str)
        
        if data_fim:
            # Converter para string se for um objeto date
            if hasattr(data_fim, 'strftime'):
                data_fim_str = data_fim.strftime('%Y-%m-%d')
            else:
                data_fim_str = data_fim
            
            query += " AND VENCIMENTO <= ?"
            params.append(data_fim_str)
        
        if status:
            # Usar TRIM para comparar sem espaços extras
            query += " AND TRIM(STATUS) = ?"
            params.append(status.strip())
        
        # Executar a consulta
        result = execute_query(query, tuple(params) if params else None)
        
        # Imprimir resultados para debug
        print(f"Query: {query}")
        print(f"Params: {params}")
        print(f"Resultados encontrados: {len(result) if result else 0}")
        
        if result and len(result) > 0:
            print(f"Primeiro resultado: {result[0]}")
            
            # Verificar se há resultados com status "Recebido"
            recebidos = [r for r in result if r[7] and r[7].strip() == 'Recebido']
            print(f"Registros com status 'Recebido': {len(recebidos)}")
            
            # Verificar os diferentes status presentes nos resultados
            status_set = set()
            for r in result:
                if r[7]:
                    status_set.add(r[7].strip())
            print(f"Status encontrados nos resultados: {status_set}")
        
        return result
    except Exception as e:
        print(f"Erro ao filtrar recebimentos: {e}")
        import traceback
        traceback.print_exc()
        return []
    
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

# Variável global para armazenar o usuário logado
usuario_logado = {
    "id": None,
    "nome": None,
    "empresa": None
}

def get_usuario_logado():
    """
    Retorna as informações do usuário logado
    
    Returns:
        dict: Dicionário com id, nome e empresa do usuário logado
    """
    global usuario_logado
    return usuario_logado

# Funções para o sistema de caixa

# def verificar_tabelas_caixa():
#     """
#     Verifica se as tabelas do sistema de caixa existem e as cria se não existirem
    
#     Returns:
#         bool: True se as tabelas existem ou foram criadas com sucesso
#     """
#     try:
#         # Verificar se a tabela CAIXA_CONTROLE existe
#         query_check = """
#         SELECT COUNT(*) FROM RDB$RELATIONS 
#         WHERE RDB$RELATION_NAME = 'CAIXA_CONTROLE'
#         """
#         result = execute_query(query_check)
        
#         # Se a tabela não existe, criar as tabelas
#         if result[0][0] == 0:
#             print("Tabelas do sistema de caixa não encontradas. Criando...")
            
#             # Criar tabela CAIXA_CONTROLE
#             query_create_controle = """
#             CREATE TABLE CAIXA_CONTROLE (
#                 ID INTEGER NOT NULL PRIMARY KEY,
#                 CODIGO VARCHAR(10) NOT NULL,
#                 DATA_ABERTURA DATE NOT NULL,
#                 HORA_ABERTURA TIME NOT NULL,
#                 DATA_FECHAMENTO DATE,
#                 HORA_FECHAMENTO TIME,
#                 VALOR_ABERTURA DECIMAL(15,2) DEFAULT 0 NOT NULL,
#                 VALOR_FECHAMENTO DECIMAL(15,2),
#                 ESTACAO VARCHAR(20) NOT NULL,
#                 ID_USUARIO INTEGER NOT NULL,
#                 USUARIO VARCHAR(50) NOT NULL,
#                 STATUS CHAR(1) DEFAULT 'A' NOT NULL,
#                 OBSERVACAO_ABERTURA VARCHAR(200),
#                 OBSERVACAO_FECHAMENTO VARCHAR(200)
#             )
#             """
#             execute_query(query_create_controle)
#             print("Tabela CAIXA_CONTROLE criada com sucesso.")
            
#             # Criar gerador de IDs para CAIXA_CONTROLE
#             try:
#                 query_generator = """
#                 CREATE GENERATOR GEN_CAIXA_CONTROLE_ID
#                 """
#                 execute_query(query_generator)
#                 print("Gerador de IDs para CAIXA_CONTROLE criado com sucesso.")
#             except Exception as e:
#                 print(f"Aviso: Gerador pode já existir: {e}")
#                 pass
            
#             # Criar trigger para CAIXA_CONTROLE
#             try:
#                 query_trigger = """
#                 CREATE TRIGGER CAIXA_CONTROLE_BI FOR CAIXA_CONTROLE
#                 ACTIVE BEFORE INSERT POSITION 0
#                 AS
#                 BEGIN
#                     IF (NEW.ID IS NULL) THEN
#                         NEW.ID = GEN_ID(GEN_CAIXA_CONTROLE_ID, 1);
#                 END
#                 """
#                 execute_query(query_trigger)
#                 print("Trigger para CAIXA_CONTROLE criado com sucesso.")
#             except Exception as e:
#                 print(f"Aviso: Trigger pode já existir: {e}")
#                 pass
            
#             # Criar tabela CAIXA_MOVIMENTOS
#             query_create_movimentos = """
#             CREATE TABLE CAIXA_MOVIMENTOS (
#                 ID INTEGER NOT NULL PRIMARY KEY,
#                 ID_CAIXA INTEGER NOT NULL,
#                 TIPO CHAR(1) NOT NULL,
#                 DATA DATE NOT NULL,
#                 HORA TIME NOT NULL,
#                 VALOR DECIMAL(15,2) NOT NULL,
#                 MOTIVO VARCHAR(50) NOT NULL,
#                 ID_USUARIO INTEGER NOT NULL,
#                 USUARIO VARCHAR(50) NOT NULL,
#                 OBSERVACAO VARCHAR(200)
#             )
#             """
#             execute_query(query_create_movimentos)
#             print("Tabela CAIXA_MOVIMENTOS criada com sucesso.")
            
#             # Criar gerador de IDs para CAIXA_MOVIMENTOS
#             try:
#                 query_generator = """
#                 CREATE GENERATOR GEN_CAIXA_MOVIMENTOS_ID
#                 """
#                 execute_query(query_generator)
#                 print("Gerador de IDs para CAIXA_MOVIMENTOS criado com sucesso.")
#             except Exception as e:
#                 print(f"Aviso: Gerador pode já existir: {e}")
#                 pass
            
#             # Criar trigger para CAIXA_MOVIMENTOS
#             try:
#                 query_trigger = """
#                 CREATE TRIGGER CAIXA_MOVIMENTOS_BI FOR CAIXA_MOVIMENTOS
#                 ACTIVE BEFORE INSERT POSITION 0
#                 AS
#                 BEGIN
#                     IF (NEW.ID IS NULL) THEN
#                         NEW.ID = GEN_ID(GEN_CAIXA_MOVIMENTOS_ID, 1);
#                 END
#                 """
#                 execute_query(query_trigger)
#                 print("Trigger para CAIXA_MOVIMENTOS criado com sucesso.")
#             except Exception as e:
#                 print(f"Aviso: Trigger pode já existir: {e}")
#                 pass
            
#             # Criar chave estrangeira para relacionar CAIXA_MOVIMENTOS com CAIXA_CONTROLE
#             try:
#                 query_fk = """
#                 ALTER TABLE CAIXA_MOVIMENTOS
#                 ADD CONSTRAINT FK_CAIXA_MOVIMENTOS_CAIXA_CONTROLE
#                 FOREIGN KEY (ID_CAIXA) REFERENCES CAIXA_CONTROLE(ID)
#                 ON DELETE CASCADE
#                 """
#                 execute_query(query_fk)
#                 print("Chave estrangeira para CAIXA_MOVIMENTOS criada com sucesso.")
#             except Exception as e:
#                 print(f"Aviso: Chave estrangeira pode já existir: {e}")
#                 pass
            
#             # Criar índices para melhorar a performance
#             try:
#                 execute_query("CREATE INDEX IDX_CAIXA_CONTROLE_CODIGO ON CAIXA_CONTROLE (CODIGO)")
#                 execute_query("CREATE INDEX IDX_CAIXA_CONTROLE_DATA_ABERTURA ON CAIXA_CONTROLE (DATA_ABERTURA)")
#                 execute_query("CREATE INDEX IDX_CAIXA_CONTROLE_STATUS ON CAIXA_CONTROLE (STATUS)")
#                 execute_query("CREATE INDEX IDX_CAIXA_MOVIMENTOS_ID_CAIXA ON CAIXA_MOVIMENTOS (ID_CAIXA)")
#                 execute_query("CREATE INDEX IDX_CAIXA_MOVIMENTOS_DATA ON CAIXA_MOVIMENTOS (DATA)")
#                 print("Índices criados com sucesso.")
#             except Exception as e:
#                 print(f"Aviso: Alguns índices podem já existir: {e}")
#                 pass
            
#             return True
#         else:
#             print("Tabelas do sistema de caixa já existem.")
        
#         return True
#     except Exception as e:
#         print(f"Erro ao verificar/criar tabelas de caixa: {e}")
#         raise Exception(f"Erro ao verificar/criar tabelas de caixa: {str(e)}")

# def abrir_caixa(codigo, data_abertura, hora_abertura, valor_abertura, estacao, observacao=None):
#     """
#     Registra a abertura de um caixa
    
#     Args:
#         codigo (str): Código do caixa
#         data_abertura (str): Data de abertura no formato DD/MM/YYYY
#         hora_abertura (str): Hora de abertura no formato HH:MM
#         valor_abertura (float): Valor inicial do caixa
#         estacao (str): Nome da estação/terminal
#         observacao (str, optional): Observação opcional
        
#     Returns:
#         int: ID do caixa aberto
#     """
#     try:
#         # Verificar se o usuário está logado
#         if not usuario_logado["id"]:
#             raise Exception("Nenhum usuário logado. Faça login antes de abrir o caixa.")
        
#         # Verificar se já existe um caixa aberto com o mesmo código
#         query_check = """
#         SELECT ID FROM CAIXA_CONTROLE 
#         WHERE CODIGO = ? AND STATUS = 'A'
#         """
#         result = execute_query(query_check, (codigo,))
        
#         if result and len(result) > 0:
#             raise Exception(f"Já existe um caixa aberto com o código {codigo}.")
        
#         # Converter data para o formato do banco (YYYY-MM-DD)
#         data_parts = data_abertura.split('/')
#         data_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
        
#         # Inserir registro de abertura de caixa
#         query_insert = """
#         INSERT INTO CAIXA_CONTROLE (
#             CODIGO, DATA_ABERTURA, HORA_ABERTURA, VALOR_ABERTURA, 
#             ESTACAO, ID_USUARIO, USUARIO, STATUS, OBSERVACAO_ABERTURA
#         ) VALUES (?, ?, ?, ?, ?, ?, ?, 'A', ?)
#         """
#         execute_query(query_insert, (
#             codigo, data_iso, hora_abertura, valor_abertura,
#             estacao, usuario_logado["id"], usuario_logado["nome"], observacao
#         ))
        
#         # Obter o ID do caixa recém-aberto
#         query_id = """
#         SELECT MAX(ID) FROM CAIXA_CONTROLE 
#         WHERE CODIGO = ? AND STATUS = 'A'
#         """
#         result = execute_query(query_id, (codigo,))
        
#         if result and len(result) > 0 and result[0][0]:
#             caixa_id = result[0][0]
            
#             # Registrar a entrada inicial como movimento
#             if valor_abertura > 0:
#                 registrar_movimento(
#                     id_caixa=caixa_id,
#                     tipo='E',  # Entrada
#                     data=data_abertura,
#                     hora=hora_abertura,
#                     valor=valor_abertura,
#                     motivo="Abertura de Caixa",
#                     observacao=observacao
#                 )
            
#             return caixa_id
#         else:
#             raise Exception("Erro ao obter o ID do caixa aberto.")
#     except Exception as e:
#         print(f"Erro ao abrir caixa: {e}")
#         raise Exception(f"Erro ao abrir caixa: {str(e)}")

# def fechar_caixa(id_caixa, data_fechamento, hora_fechamento, valor_fechamento, observacao=None):
#     """
#     Registra o fechamento de um caixa
    
#     Args:
#         id_caixa (int): ID do caixa a ser fechado
#         data_fechamento (str): Data de fechamento no formato DD/MM/YYYY
#         hora_fechamento (str): Hora de fechamento no formato HH:MM
#         valor_fechamento (float): Valor final do caixa
#         observacao (str, optional): Observação opcional
        
#     Returns:
#         bool: True se o caixa foi fechado com sucesso
#     """
#     try:
#         # Verificar se o usuário está logado
#         if not usuario_logado["id"]:
#             raise Exception("Nenhum usuário logado. Faça login antes de fechar o caixa.")
        
#         # Verificar se o caixa existe e está aberto
#         query_check = """
#         SELECT ID, CODIGO, VALOR_ABERTURA FROM CAIXA_CONTROLE 
#         WHERE ID = ? AND STATUS = 'A'
#         """
#         result = execute_query(query_check, (id_caixa,))
        
#         if not result or len(result) == 0:
#             raise Exception(f"Caixa com ID {id_caixa} não encontrado ou já está fechado.")
        
#         codigo_caixa = result[0][1]
#         valor_abertura = float(result[0][2])  # Convertendo para float
        
#         # Converter data para o formato do banco (YYYY-MM-DD)
#         data_parts = data_fechamento.split('/')
#         data_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
        
#         # Atualizar registro para fechar o caixa
#         query_update = """
#         UPDATE CAIXA_CONTROLE SET
#             DATA_FECHAMENTO = ?,
#             HORA_FECHAMENTO = ?,
#             VALOR_FECHAMENTO = ?,
#             STATUS = 'F',
#             OBSERVACAO_FECHAMENTO = ?
#         WHERE ID = ?
#         """
#         execute_query(query_update, (
#             data_iso, hora_fechamento, valor_fechamento,
#             observacao, id_caixa
#         ))
        
#         # Registrar o fechamento como movimento (se houver diferença)
#         diferenca = valor_fechamento - valor_abertura
        
#         if diferenca != 0:
#             tipo = 'E' if diferenca > 0 else 'S'  # Entrada ou Saída
#             valor_movimento = abs(diferenca)
#             motivo = "Fechamento de Caixa"
            
#             registrar_movimento(
#                 id_caixa=id_caixa,
#                 tipo=tipo,
#                 data=data_fechamento,
#                 hora=hora_fechamento,
#                 valor=valor_movimento,
#                 motivo=motivo,
#                 observacao=observacao
#             )
        
#         return True
#     except Exception as e:
#         print(f"Erro ao fechar caixa: {e}")
#         raise Exception(f"Erro ao fechar caixa: {str(e)}")

# def obter_turno_ativo():
#     """Retorna o turno ativo (sem data de fechamento)"""
#     try:
#         query = """
#         SELECT ID, CODIGO, DATA_ABERTURA, HORA_ABERTURA, VALOR_ABERTURA, 
#                ESTACAO, USUARIO, ID_USUARIO
#         FROM CAIXA_CONTROLE 
#         WHERE DATA_FECHAMENTO IS NULL 
#         ORDER BY ID DESC 
#         LIMIT 1
#         """
        
#         result = execute_query(query)
        
#         if result and len(result) > 0:
#             turno = result[0]
#             return {
#                 'id': turno[0],
#                 'codigo': turno[1],
#                 'data_abertura': turno[2],
#                 'hora_abertura': turno[3],
#                 'valor_abertura': float(turno[4]) if turno[4] else 0.0,
#                 'estacao': turno[5],
#                 'usuario': turno[6],
#                 'usuario_id': turno[7]
#             }
        
#         return None
        
#     except Exception as e:
#         print(f"Erro ao obter turno ativo: {e}")
#         return None

# def registrar_venda_caixa(turno_id, numero_venda, valor_total, forma_pagamento, operador_id=None):
#     """Registra uma venda no controle de caixa"""
#     try:
#         if not operador_id:
#             usuario = get_usuario_logado()
#             operador_id = usuario.get("id") if usuario else None
            
#         if not operador_id:
#             operador_id = 1  # ID padrão se não conseguir obter
        
#         # Data e hora atuais
#         from datetime import datetime
#         agora = datetime.now()
#         data_venda = agora.strftime("%d/%m/%Y")
#         hora_venda = agora.strftime("%H:%M")
        
#         # Registrar venda na tabela CAIXA_VENDAS (se existir)
#         try:
#             query_venda = """
#             INSERT INTO CAIXA_VENDAS 
#             (TURNO_ID, NUMERO_VENDA, VALOR_TOTAL, FORMA_PAGAMENTO, 
#              DATA_VENDA, HORA_VENDA, OPERADOR_ID)
#             VALUES (?, ?, ?, ?, ?, ?, ?)
#             """
            
#             params_venda = (
#                 turno_id, numero_venda, valor_total, forma_pagamento,
#                 data_venda, hora_venda, operador_id
#             )
            
#             execute_query(query_venda, params_venda)
#             print(f"✅ Venda registrada na tabela CAIXA_VENDAS")
            
#         except Exception as e:
#             print(f"⚠️ Tabela CAIXA_VENDAS não existe ou erro: {e}")
        
#         # Registrar como movimentação na tabela CAIXA_MOVIMENTACOES (se existir)
#         try:
#             query_mov = """
#             INSERT INTO CAIXA_MOVIMENTACOES 
#             (TURNO_ID, TIPO, FORMA_PAGAMENTO, VALOR, MOTIVO, OBSERVACAO, 
#              DATA_MOVIMENTO, HORA_MOVIMENTO, USUARIO_ID)
#             VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#             """
            
#             params_mov = (
#                 turno_id, "venda", forma_pagamento, valor_total,
#                 f"Venda Nº {numero_venda}", None,
#                 data_venda, hora_venda, operador_id
#             )
            
#             execute_query(query_mov, params_mov)
#             print(f"✅ Movimentação registrada na tabela CAIXA_MOVIMENTACOES")
            
#         except Exception as e:
#             print(f"⚠️ Tabela CAIXA_MOVIMENTACOES não existe ou erro: {e}")
        
#         print(f"✅ Venda {numero_venda} registrada no controle de caixa - Turno {turno_id}")
#         return True
        
#     except Exception as e:
#         print(f"❌ Erro ao registrar venda no caixa: {e}")
#         # NÃO propagar o erro - não quebrar a venda
#         return False

# Função auxiliar se não existir
def get_usuario_logado():
    """Retorna o usuário logado ou dados padrão"""
    try:
        # Se você tem uma variável global para usuário logado
        if hasattr(get_usuario_logado, 'usuario_atual'):
            return get_usuario_logado.usuario_atual
        
        # Retornar dados padrão
        return {"id": 1, "nome": "Operador PDV"}
        
    except:
        return {"id": 1, "nome": "Operador PDV"}

def registrar_movimento(id_caixa, tipo, data, hora, valor, motivo, observacao=None):
    """
    Registra um movimento de entrada ou saída no caixa
    
    Args:
        id_caixa (int): ID do caixa
        tipo (str): Tipo de movimento (E=Entrada, S=Saída)
        data (str): Data do movimento no formato DD/MM/YYYY
        hora (str): Hora do movimento no formato HH:MM
        valor (float): Valor do movimento
        motivo (str): Motivo do movimento
        observacao (str, optional): Observação opcional
        
    Returns:
        int: ID do movimento registrado
    """
    try:
        # Verificar se o usuário está logado
        if not usuario_logado["id"]:
            raise Exception("Nenhum usuário logado. Faça login antes de registrar movimentos.")
        
        # Verificar se o caixa existe e está aberto
        query_check = """
        SELECT ID FROM CAIXA_CONTROLE 
        WHERE ID = ? AND STATUS = 'A'
        """
        result = execute_query(query_check, (id_caixa,))
        
        if not result or len(result) == 0:
            raise Exception(f"Caixa com ID {id_caixa} não encontrado ou já está fechado.")
        
        # Converter data para o formato do banco (YYYY-MM-DD)
        data_parts = data.split('/')
        data_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
        
        # Inserir registro de movimento
        query_insert = """
        INSERT INTO CAIXA_MOVIMENTOS (
            ID_CAIXA, TIPO, DATA, HORA, VALOR, 
            MOTIVO, ID_USUARIO, USUARIO, OBSERVACAO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        execute_query(query_insert, (
            id_caixa, tipo, data_iso, hora, valor,
            motivo, usuario_logado["id"], usuario_logado["nome"], observacao
        ))
        
        # Obter o ID do movimento recém-registrado
        query_id = """
        SELECT MAX(ID) FROM CAIXA_MOVIMENTOS 
        WHERE ID_CAIXA = ?
        """
        result = execute_query(query_id, (id_caixa,))
        
        if result and len(result) > 0 and result[0][0]:
            return result[0][0]
        else:
            raise Exception("Erro ao obter o ID do movimento registrado.")
    except Exception as e:
        print(f"Erro ao registrar movimento: {e}")
        raise Exception(f"Erro ao registrar movimento: {str(e)}")

def listar_caixas(data_inicial=None, data_final=None, status=None, codigo=None, estacao=None, usuario=None):
    """
    Lista os caixas registrados com base nos filtros informados
    
    Args:
        data_inicial (str, optional): Data inicial no formato DD/MM/YYYY
        data_final (str, optional): Data final no formato DD/MM/YYYY
        status (str, optional): Status do caixa (A=Aberto, F=Fechado)
        codigo (str, optional): Código do caixa
        estacao (str, optional): Nome da estação
        usuario (str, optional): Nome do usuário
        
    Returns:
        list: Lista de caixas encontrados
    """
    try:
        # Construir a query base
        query = """
        SELECT 
            ID, CODIGO, 
            DATA_ABERTURA, HORA_ABERTURA, 
            DATA_FECHAMENTO, HORA_FECHAMENTO, 
            VALOR_ABERTURA, VALOR_FECHAMENTO, 
            ESTACAO, USUARIO, STATUS
        FROM CAIXA_CONTROLE
        WHERE 1=1
        """
        params = []
        
        # Adicionar filtros se informados
        if data_inicial:
            data_parts = data_inicial.split('/')
            data_inicial_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
            query += " AND DATA_ABERTURA >= ?"
            params.append(data_inicial_iso)
        
        if data_final:
            data_parts = data_final.split('/')
            data_final_iso = f"{data_parts[2]}-{data_parts[1]}-{data_parts[0]}"
            query += " AND DATA_ABERTURA <= ?"
            params.append(data_final_iso)
        
        if status:
            query += " AND STATUS = ?"
            params.append(status)
        
        if codigo:
            query += " AND CODIGO = ?"
            params.append(codigo)
        
        if estacao:
            query += " AND ESTACAO LIKE ?"
            params.append(f"%{estacao}%")
        
        if usuario:
            query += " AND USUARIO LIKE ?"
            params.append(f"%{usuario}%")
        
        # Ordenar por data de abertura decrescente
        query += " ORDER BY DATA_ABERTURA DESC, HORA_ABERTURA DESC"
        
        # Executar a query
        result = execute_query(query, tuple(params) if params else None)
        
        # Formatar as datas para o formato DD/MM/YYYY
        formatted_result = []
        for row in result:
            # Converter datas para o formato brasileiro
            data_abertura = row[2]
            if data_abertura:
                data_abertura = f"{data_abertura.day:02d}/{data_abertura.month:02d}/{data_abertura.year}"
            
            data_fechamento = row[4]
            if data_fechamento:
                data_fechamento = f"{data_fechamento.day:02d}/{data_fechamento.month:02d}/{data_fechamento.year}"
            
            # Criar nova tupla com os dados formatados
            formatted_row = (
                row[0],  # ID
                row[1],  # CODIGO
                data_abertura,  # DATA_ABERTURA formatada
                row[3],  # HORA_ABERTURA
                data_fechamento,  # DATA_FECHAMENTO formatada
                row[5],  # HORA_FECHAMENTO
                row[6],  # VALOR_ABERTURA
                row[7],  # VALOR_FECHAMENTO
                row[8],  # ESTACAO
                row[9],  # USUARIO
                row[10]  # STATUS
            )
            formatted_result.append(formatted_row)
        
        return formatted_result
    except Exception as e:
        print(f"Erro ao listar caixas: {e}")
        raise Exception(f"Erro ao listar caixas: {str(e)}")
@functools.lru_cache(maxsize=512)
def obter_caixa_por_id(id_caixa):
    """
    Obtém os dados de um caixa específico pelo ID
    
    Args:
        id_caixa (int): ID do caixa
        
    Returns:
        tuple: Dados do caixa ou None se não encontrado
    """
    try:
        query = """
        SELECT 
            ID, CODIGO, 
            DATA_ABERTURA, HORA_ABERTURA, 
            DATA_FECHAMENTO, HORA_FECHAMENTO, 
            VALOR_ABERTURA, VALOR_FECHAMENTO, 
            ESTACAO, USUARIO, STATUS,
            OBSERVACAO_ABERTURA, OBSERVACAO_FECHAMENTO
        FROM CAIXA_CONTROLE
        WHERE ID = ?
        """
        result = execute_query(query, (id_caixa,))
        
        if result and len(result) > 0:
            row = result[0]
            
            # Converter datas para o formato brasileiro
            data_abertura = row[2]
            if data_abertura:
                data_abertura = f"{data_abertura.day:02d}/{data_abertura.month:02d}/{data_abertura.year}"
            
            data_fechamento = row[4]
            if data_fechamento:
                data_fechamento = f"{data_fechamento.day:02d}/{data_fechamento.month:02d}/{data_fechamento.year}"
            
            # Criar nova tupla com os dados formatados
            formatted_row = (
                row[0],  # ID
                row[1],  # CODIGO
                data_abertura,  # DATA_ABERTURA formatada
                row[3],  # HORA_ABERTURA
                data_fechamento,  # DATA_FECHAMENTO formatada
                row[5],  # HORA_FECHAMENTO
                row[6],  # VALOR_ABERTURA
                row[7],  # VALOR_FECHAMENTO
                row[8],  # ESTACAO
                row[9],  # USUARIO
                row[10],  # STATUS
                row[11],  # OBSERVACAO_ABERTURA
                row[12]   # OBSERVACAO_FECHAMENTO
            )
            
            return formatted_row
        
        return None
    except Exception as e:
        print(f"Erro ao obter caixa: {e}")
        raise Exception(f"Erro ao obter caixa: {str(e)}")

def listar_movimentos_caixa(id_caixa):
    """
    Lista os movimentos de um caixa específico
    
    Args:
        id_caixa (int): ID do caixa
        
    Returns:
        list: Lista de movimentos do caixa
    """
    try:
        query = """
        SELECT 
            ID, TIPO, DATA, HORA, VALOR, 
            MOTIVO, USUARIO, OBSERVACAO
        FROM CAIXA_MOVIMENTOS
        WHERE ID_CAIXA = ?
        ORDER BY DATA, HORA
        """
        result = execute_query(query, (id_caixa,))
        
        # Formatar as datas para o formato DD/MM/YYYY
        formatted_result = []
        for row in result:
            # Converter data para o formato brasileiro
            data = row[2]
            if data:
                data = f"{data.day:02d}/{data.month:02d}/{data.year}"
            
            # Criar nova tupla com os dados formatados
            formatted_row = (
                row[0],  # ID
                row[1],  # TIPO
                data,    # DATA formatada
                row[3],  # HORA
                row[4],  # VALOR
                row[5],  # MOTIVO
                row[6],  # USUARIO
                row[7]   # OBSERVACAO
            )
            formatted_result.append(formatted_row)
        
        return formatted_result
    except Exception as e:
        print(f"Erro ao listar movimentos: {e}")
        raise Exception(f"Erro ao listar movimentos: {str(e)}")

def obter_proximo_codigo_caixa():
    """
    Obtém o próximo código disponível para um novo caixa
    
    Returns:
        str: Próximo código de caixa disponível (formato: 001, 002, etc.)
    """
    try:
        query = """
        SELECT MAX(CAST(CODIGO AS INTEGER)) FROM CAIXA_CONTROLE
        """
        result = execute_query(query)
        
        if result and len(result) > 0 and result[0][0] is not None:
            proximo_codigo = int(result[0][0]) + 1
        else:
            proximo_codigo = 1
        
        # Formatar com zeros à esquerda (001, 002, etc.)
        return f"{proximo_codigo:03d}"
    except Exception as e:
        print(f"Erro ao obter próximo código: {e}")
        # Em caso de erro, retorna um código padrão
        return "001"
    
#Baco de relatorio de vendas
# Funções para o sistema de relatório de vendas de produtos

def verificar_tabela_vendas_produtos():
    """
    Verifica se as tabelas do sistema de vendas de produtos existem e as cria se não existirem
    
    Returns:
        bool: True se as tabelas existem ou foram criadas com sucesso
    """
    try:
        # Verificar se a tabela VENDAS_PRODUTOS existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'VENDAS_PRODUTOS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, criar as tabelas
        if result[0][0] == 0:
            print("Tabelas do sistema de vendas de produtos não encontradas. Criando...")
            
            # Criar tabela VENDAS_PRODUTOS
            query_create = """
            CREATE TABLE VENDAS_PRODUTOS (
                ID INTEGER NOT NULL PRIMARY KEY,
                DATA DATE NOT NULL,
                CODIGO_PRODUTO VARCHAR(20) NOT NULL,
                PRODUTO VARCHAR(100) NOT NULL,
                CATEGORIA VARCHAR(50),
                QUANTIDADE DECIMAL(15,3) NOT NULL,
                VALOR_UNITARIO DECIMAL(15,2) NOT NULL,
                VALOR_TOTAL DECIMAL(15,2) NOT NULL,
                CLIENTE VARCHAR(100),
                VENDEDOR VARCHAR(100)
            )
            """
            execute_query(query_create)
            print("Tabela VENDAS_PRODUTOS criada com sucesso.")
            
            # Criar gerador de IDs para VENDAS_PRODUTOS
            try:
                query_generator = """
                CREATE GENERATOR GEN_VENDAS_PRODUTOS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs para VENDAS_PRODUTOS criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
                pass
            
            # Criar trigger para VENDAS_PRODUTOS
            try:
                query_trigger = """
                CREATE TRIGGER VENDAS_PRODUTOS_BI FOR VENDAS_PRODUTOS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_VENDAS_PRODUTOS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger para VENDAS_PRODUTOS criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                pass
            
            # Criar índices para melhorar a performance
            try:
                execute_query("CREATE INDEX IDX_VENDAS_PRODUTOS_DATA ON VENDAS_PRODUTOS (DATA)")
                execute_query("CREATE INDEX IDX_VENDAS_PRODUTOS_PRODUTO ON VENDAS_PRODUTOS (CODIGO_PRODUTO)")
                execute_query("CREATE INDEX IDX_VENDAS_PRODUTOS_CATEGORIA ON VENDAS_PRODUTOS (CATEGORIA)")
                print("Índices criados com sucesso.")
            except Exception as e:
                print(f"Aviso: Alguns índices podem já existir: {e}")
                pass
            
            # Inserir dados de exemplo
            inserir_dados_exemplo_vendas()
            
            return True
        else:
            print("Tabelas do sistema de vendas de produtos já existem.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabelas de vendas de produtos: {e}")
        raise Exception(f"Erro ao verificar/criar tabelas de vendas de produtos: {str(e)}")

def atualizar_estoque_apos_venda(codigo_produto, quantidade_vendida):
    """
    Atualiza o estoque de um produto após uma venda
    
    Args:
        codigo_produto (str): Código do produto vendido
        quantidade_vendida (float): Quantidade vendida
        
    Returns:
        bool: True se a atualização foi bem-sucedida, False caso contrário
        dict: Informações sobre o estoque após a atualização, incluindo avisos se necessário
    """
    try:
        # Buscar o produto pelo código
        produto = buscar_produto_por_codigo(codigo_produto)
        
        if not produto:
            raise Exception(f"Produto com código {codigo_produto} não encontrado")
        
        # Obter o estoque atual e calcular o novo estoque
        id_produto = produto[0]
        estoque_atual = produto[8] or 0  # Índice 8 é QUANTIDADE_ESTOQUE
        
        if estoque_atual < quantidade_vendida:
            raise Exception(f"Estoque insuficiente. Disponível: {estoque_atual}, Solicitado: {quantidade_vendida}")
        
        novo_estoque = estoque_atual - quantidade_vendida
        
        # Atualizar o estoque do produto
        query = """
        UPDATE PRODUTOS
        SET QUANTIDADE_ESTOQUE = ?
        WHERE ID = ?
        """
        
        execute_query(query, (novo_estoque, id_produto))
        
        # Verificar se o estoque está baixo
        resultado = {
            "sucesso": True,
            "produto": produto[2],  # Nome do produto
            "estoque_anterior": estoque_atual,
            "estoque_atual": novo_estoque,
            "estoque_baixo": False,
            "mensagem": "Estoque atualizado com sucesso."
        }
        
        # Definir limites para estoque baixo (pode ajustar conforme necessário)
        limite_estoque_baixo = 5  # Exemplo: avisar quando estoque for menor que 5
        
        if novo_estoque <= limite_estoque_baixo:
            resultado["estoque_baixo"] = True
            resultado["mensagem"] = f"ATENÇÃO: Estoque baixo para o produto {produto[2]}. Restam apenas {novo_estoque} unidades. É necessário repor!"
            
            # Registrar o alerta de estoque baixo (opcional)
            registrar_alerta_estoque_baixo(produto[0], produto[2], novo_estoque)
        
        return resultado
    
    except Exception as e:
        print(f"Erro ao atualizar estoque: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao atualizar estoque: {str(e)}"
        }
    
def registrar_alerta_estoque_baixo(id_produto, nome_produto, estoque_atual):
    """
    Registra um alerta de estoque baixo (pode ser adaptado para
    salvar em uma tabela de alertas, enviar e-mail, etc.)
    
    Args:
        id_produto (int): ID do produto
        nome_produto (str): Nome do produto
        estoque_atual (float): Quantidade atual em estoque
    """
    # Esta é uma implementação simples que apenas imprime o alerta no console
    # Você pode expandir para salvar em um log ou tabela, enviar e-mail, etc.
    print(f"[ALERTA] Estoque baixo: Produto {nome_produto} (ID: {id_produto}) - Restam apenas {estoque_atual} unidades.")
    
    # Implementação futura: salvar em uma tabela de alertas
    # Por exemplo:
    # inserir_alerta_tabela(id_produto, nome_produto, estoque_atual, datetime.now())

def verificar_produtos_estoque_baixo(limite=5):
    """
    Verifica todos os produtos com estoque baixo
    
    Args:
        limite (int): Limite para considerar estoque baixo
        
    Returns:
        list: Lista de produtos com estoque baixo
    """
    try:
        query = """
        SELECT ID, CODIGO, NOME, QUANTIDADE_ESTOQUE
        FROM PRODUTOS
        WHERE QUANTIDADE_ESTOQUE <= ?
        ORDER BY QUANTIDADE_ESTOQUE
        """
        
        result = execute_query(query, (limite,))
        
        # Formatar os resultados
        produtos_estoque_baixo = []
        for produto in result:
            produtos_estoque_baixo.append({
                "id": produto[0],
                "codigo": produto[1],
                "nome": produto[2],
                "estoque": produto[3]
            })
        
        return produtos_estoque_baixo
        
    except Exception as e:
        print(f"Erro ao verificar produtos com estoque baixo: {e}")
        return []


def inserir_dados_exemplo_vendas():
    """
    Insere dados de exemplo para o relatório de vendas de produtos
    """
    try:
        # Verificar se já existem dados na tabela
        query_check = "SELECT COUNT(*) FROM VENDAS_PRODUTOS"
        result = execute_query(query_check)
        
        if result[0][0] > 0:
            print("Tabela VENDAS_PRODUTOS já possui dados. Pulando inserção de exemplos.")
            return
        
        # Buscar produtos existentes no banco
        produtos = listar_produtos()
        
        if not produtos or len(produtos) == 0:
            print("Nenhum produto encontrado para criar vendas exemplo.")
            return
        
        # Gerar datas para os últimos 30 dias
        import datetime
        hoje = datetime.datetime.now().date()
        datas = [(hoje - datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(30)]
        
        # Inserir vendas aleatórias para os últimos 30 dias
        import random
        
        for _ in range(50):  # Inserir 50 vendas aleatórias
            # Escolher um produto aleatório
            produto = random.choice(produtos)
            codigo_produto = produto[1]  # Índice 1 é o código do produto
            nome_produto = produto[2]    # Índice 2 é o nome do produto
            grupo = produto[5] if len(produto) > 5 and produto[5] else 'Sem Categoria'
            
            # Escolher uma data aleatória
            data = random.choice(datas)
            
            # Dados aleatórios de venda
            quantidade = random.randint(1, 10)
            valor_unitario = float(produto[7]) if len(produto) > 7 and produto[7] else random.uniform(10.0, 100.0)
            valor_total = quantidade * valor_unitario
            
            # Clientes e vendedores fictícios
            clientes = ["João Silva", "Maria Souza", "Pedro Oliveira", "Ana Santos", "Carla Lima"]
            vendedores = ["Vendedor 1", "Vendedor 2", "Vendedor 3"]
            
            cliente = random.choice(clientes)
            vendedor = random.choice(vendedores)
            
            # Inserir a venda
            query_insert = """
            INSERT INTO VENDAS_PRODUTOS (
                DATA, CODIGO_PRODUTO, PRODUTO, CATEGORIA, QUANTIDADE,
                VALOR_UNITARIO, VALOR_TOTAL, CLIENTE, VENDEDOR
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            execute_query(query_insert, (
                data, codigo_produto, nome_produto, grupo, quantidade,
                valor_unitario, valor_total, cliente, vendedor
            ))
        
        print(f"Inseridos {50} registros de vendas de exemplo.")
        return True
        
    except Exception as e:
        print(f"Erro ao inserir dados de exemplo de vendas: {e}")
        return False

def registrar_venda_produto(data, codigo_produto, produto, categoria, quantidade, 
                           valor_unitario, valor_total, cliente=None, vendedor=None):
    """
    Registra uma venda de produto
    
    Args:
        data (str): Data da venda no formato YYYY-MM-DD
        codigo_produto (str): Código do produto
        produto (str): Nome do produto
        categoria (str): Categoria/grupo do produto
        quantidade (float): Quantidade vendida
        valor_unitario (float): Valor unitário
        valor_total (float): Valor total
        cliente (str, optional): Nome do cliente
        vendedor (str, optional): Nome do vendedor
        
    Returns:
        int: ID da venda registrada
    """
    try:
        # Inserir a venda
        query = """
        INSERT INTO VENDAS_PRODUTOS (
            DATA, CODIGO_PRODUTO, PRODUTO, CATEGORIA, QUANTIDADE,
            VALOR_UNITARIO, VALOR_TOTAL, CLIENTE, VENDEDOR
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        execute_query(query, (
            data, codigo_produto, produto, categoria, quantidade,
            valor_unitario, valor_total, cliente, vendedor
        ))
        
        # Obter o ID da venda recém-registrada
        query_id = "SELECT MAX(ID) FROM VENDAS_PRODUTOS"
        result = execute_query(query_id)
        
        if result and len(result) > 0 and result[0][0]:
            return result[0][0]
        
        return None
    except Exception as e:
        print(f"Erro ao registrar venda: {e}")
        raise Exception(f"Erro ao registrar venda: {str(e)}")

def obter_vendas_por_periodo(data_inicial, data_final, categoria=None):
    """
    Obtém as vendas de produtos em um período
    
    Args:
        data_inicial (str): Data inicial no formato YYYY-MM-DD
        data_final (str): Data final no formato YYYY-MM-DD
        categoria (str, optional): Categoria para filtrar
        
    Returns:
        list: Lista de dicionários com os dados das vendas
    """
    try:
        # Construir a query
        query = """
        SELECT 
            PRODUTO, CATEGORIA, DATA, QUANTIDADE, VALOR_TOTAL
        FROM VENDAS_PRODUTOS
        WHERE DATA BETWEEN ? AND ?
        """
        
        params = [data_inicial, data_final]
        
        # Adicionar filtro de categoria se fornecido
        if categoria:
            query += " AND CATEGORIA = ?"
            params.append(categoria)
        
        # Ordenar por data e produto
        query += " ORDER BY DATA, PRODUTO"
        
        # Executar a query
        result = execute_query(query, tuple(params))
        
        # Converter para lista de dicionários
        vendas = []
        for row in result:
            vendas.append({
                "produto": row[0],
                "categoria": row[1],
                "data": row[2],
                "quantidade": row[3],
                "valor_total": row[4]
            })
        
        return vendas
    except Exception as e:
        print(f"Erro ao obter vendas por período: {e}")
        raise Exception(f"Erro ao obter vendas por período: {str(e)}")

def obter_resumo_vendas_por_periodo(data_inicial, data_final, categoria=None):
    """
    Obtém um resumo das vendas agregadas por produto
    
    Args:
        data_inicial (str): Data inicial no formato YYYY-MM-DD
        data_final (str): Data final no formato YYYY-MM-DD
        categoria (str, optional): Categoria para filtrar
        
    Returns:
        list: Lista de dicionários com o resumo das vendas
    """
    try:
        # Construir a query
        query = """
        SELECT 
            PRODUTO, CATEGORIA, 
            SUM(QUANTIDADE) as QUANTIDADE_TOTAL, 
            SUM(VALOR_TOTAL) as VALOR_TOTAL,
            COUNT(*) as NUM_VENDAS
        FROM VENDAS_PRODUTOS
        WHERE DATA BETWEEN ? AND ?
        """
        
        params = [data_inicial, data_final]
        
        # Adicionar filtro de categoria se fornecido
        if categoria:
            query += " AND CATEGORIA = ?"
            params.append(categoria)
        
        # Agrupar por produto e categoria
        query += " GROUP BY PRODUTO, CATEGORIA"
        
        # Ordenar por quantidade total (decrescente)
        query += " ORDER BY QUANTIDADE_TOTAL DESC"
        
        # Executar a query
        result = execute_query(query, tuple(params))
        
        # Converter para lista de dicionários
        resumo = []
        for row in result:
            resumo.append({
                "produto": row[0],
                "categoria": row[1],
                "quantidade_total": row[2],
                "valor_total": row[3],
                "num_vendas": row[4]
            })
        
        return resumo
    except Exception as e:
        print(f"Erro ao obter resumo de vendas: {e}")
        raise Exception(f"Erro ao obter resumo de vendas: {str(e)}")

#Conta Corrente
# Add this function to your banco.py file

def verificar_tabela_contas_correntes():
    """
    Verifica se a tabela CONTAS_CORRENTES existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'CONTAS_CORRENTES'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela CONTAS_CORRENTES não encontrada. Criando...")
            query_create = """
            CREATE TABLE CONTAS_CORRENTES (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(20) NOT NULL,
                DESCRICAO VARCHAR(100) NOT NULL,
                BANCO VARCHAR(20),
                BANCO_DESCRICAO VARCHAR(100),
                CAIXA_PDV CHAR(1) DEFAULT 'N',
                AGENCIA VARCHAR(20),
                CONTA VARCHAR(20),
                SALDO DECIMAL(15,2) DEFAULT 0
            )
            """
            execute_query(query_create)
            print("Tabela CONTAS_CORRENTES criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_CONTAS_CORRENTES_ID
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
                CREATE TRIGGER CONTAS_CORRENTES_BI FOR CONTAS_CORRENTES
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_CONTAS_CORRENTES_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            # Dados iniciais
            dados_iniciais = [
                ("001", "CARTEIRA", "1", "LOCAL", "S", "", "", 0.00),
                ("002", "CAIXA", "1", "LOCAL", "S", "", "", 0.00)
            ]
            
            for conta in dados_iniciais:
                try:
                    query_insert = """
                    INSERT INTO CONTAS_CORRENTES 
                    (CODIGO, DESCRICAO, BANCO, BANCO_DESCRICAO, CAIXA_PDV, AGENCIA, CONTA, SALDO) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """
                    execute_query(query_insert, conta)
                    print(f"Conta {conta[0]} - {conta[1]} inserida com sucesso.")
                except Exception as e:
                    print(f"Erro ao inserir conta {conta[0]}: {e}")
            
            return True
        else:
            print("Tabela CONTAS_CORRENTES já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de contas correntes: {str(e)}")

def listar_contas_correntes():
    """
    Lista todas as contas correntes cadastradas
    
    Returns:
        list: Lista de tuplas com dados das contas correntes
    """
    try:
        query = """
        SELECT ID, CODIGO, DESCRICAO, BANCO, BANCO_DESCRICAO, CAIXA_PDV
        FROM CONTAS_CORRENTES
        ORDER BY CODIGO
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar contas correntes: {e}")
        raise Exception(f"Erro ao listar contas correntes: {str(e)}")
@functools.lru_cache(maxsize=512)
def buscar_conta_corrente_por_id(id_conta):
    """
    Busca uma conta corrente pelo ID
    
    Args:
        id_conta (int): ID da conta corrente
        
    Returns:
        tuple: Dados da conta corrente ou None se não encontrada
    """
    try:
        query = """
        SELECT * FROM CONTAS_CORRENTES
        WHERE ID = ?
        """
        result = execute_query(query, (id_conta,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar conta corrente: {e}")
        raise Exception(f"Erro ao buscar conta corrente: {str(e)}")

def buscar_conta_corrente_por_codigo(codigo):
    """
    Busca uma conta corrente pelo código
    
    Args:
        codigo (str): Código da conta corrente
        
    Returns:
        tuple: Dados da conta corrente ou None se não encontrada
    """
    try:
        query = """
        SELECT * FROM CONTAS_CORRENTES
        WHERE CODIGO = ?
        """
        result = execute_query(query, (codigo,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar conta corrente por código: {e}")
        raise Exception(f"Erro ao buscar conta corrente por código: {str(e)}")

def criar_conta_corrente(codigo, descricao, banco, banco_descricao, caixa_pdv="N", agencia="", conta="", saldo=0.00):
    """
    Cria uma nova conta corrente no banco de dados
    
    Args:
        codigo (str): Código da conta corrente
        descricao (str): Descrição da conta
        banco (str): Código do banco
        banco_descricao (str): Descrição do banco
        caixa_pdv (str, optional): Se é caixa PDV (S/N)
        agencia (str, optional): Número da agência
        conta (str, optional): Número da conta
        saldo (float, optional): Saldo inicial
        
    Returns:
        int: ID da conta corrente criada
    """
    try:
        # Verificar se já existe uma conta com o mesmo código
        conta_existente = buscar_conta_corrente_por_codigo(codigo)
        if conta_existente:
            raise Exception(f"Já existe uma conta corrente cadastrada com o código {codigo}")
        
        # Garantir que todos os parâmetros não são None
        codigo = str(codigo).strip() if codigo else ""
        descricao = str(descricao).strip() if descricao else ""
        banco = str(banco).strip() if banco else ""
        banco_descricao = str(banco_descricao).strip() if banco_descricao else ""
        caixa_pdv = "S" if caixa_pdv == True or caixa_pdv == "S" else "N"
        agencia = str(agencia).strip() if agencia else ""
        conta = str(conta).strip() if conta else ""
        
        # Converter saldo para float
        try:
            saldo_float = float(saldo)
        except (ValueError, TypeError):
            saldo_float = 0.00
        
        # Inserir a conta corrente
        query = """
        INSERT INTO CONTAS_CORRENTES (
            CODIGO, DESCRICAO, BANCO, BANCO_DESCRICAO, CAIXA_PDV, AGENCIA, CONTA, SALDO
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        params = (
            codigo, descricao, banco, banco_descricao, caixa_pdv, agencia, conta, saldo_float
        )
        
        execute_query(query, params)
        
        # Retornar o ID da conta inserida
        conta_inserida = buscar_conta_corrente_por_codigo(codigo)
        if conta_inserida:
            return conta_inserida[0]  # ID é o primeiro item da tupla
        
        return None
    except Exception as e:
        print(f"Erro ao criar conta corrente: {e}")
        raise Exception(f"Erro ao criar conta corrente: {str(e)}")

def atualizar_conta_corrente(id_conta, codigo, descricao, banco, banco_descricao, caixa_pdv="N", agencia="", conta="", saldo=None):
    """
    Atualiza uma conta corrente existente
    
    Args:
        id_conta (int): ID da conta corrente a ser atualizada
        codigo (str): Código da conta corrente
        descricao (str): Descrição da conta
        banco (str): Código do banco
        banco_descricao (str): Descrição do banco
        caixa_pdv (str, optional): Se é caixa PDV (S/N)
        agencia (str, optional): Número da agência
        conta (str, optional): Número da conta
        saldo (float, optional): Saldo da conta (passar None para não alterar)
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se a conta existe
        conta_existente = buscar_conta_corrente_por_id(id_conta)
        if not conta_existente:
            raise Exception(f"Conta corrente com ID {id_conta} não encontrada")
        
        # Verificar se o código sendo alterado já está em uso
        if codigo != conta_existente[1]:  # Comparar com o código atual (índice 1)
            outra_conta = buscar_conta_corrente_por_codigo(codigo)
            if outra_conta:
                raise Exception(f"Já existe outra conta corrente com o código {codigo}")
        
        # Garantir que os parâmetros não são None
        codigo = str(codigo).strip() if codigo else ""
        descricao = str(descricao).strip() if descricao else ""
        banco = str(banco).strip() if banco else ""
        banco_descricao = str(banco_descricao).strip() if banco_descricao else ""
        caixa_pdv = "S" if caixa_pdv == True or caixa_pdv == "S" else "N"
        agencia = str(agencia).strip() if agencia else ""
        conta = str(conta).strip() if conta else ""
        
        # Construir a query de atualização
        campos = [
            "CODIGO = ?",
            "DESCRICAO = ?",
            "BANCO = ?",
            "BANCO_DESCRICAO = ?",
            "CAIXA_PDV = ?",
            "AGENCIA = ?",
            "CONTA = ?"
        ]
        
        params = [
            codigo, descricao, banco, banco_descricao, caixa_pdv, agencia, conta
        ]
        
        # Adicionar o saldo se for fornecido
        if saldo is not None:
            try:
                saldo_float = float(saldo)
                campos.append("SALDO = ?")
                params.append(saldo_float)
            except (ValueError, TypeError):
                pass  # Ignorar se não for possível converter
        
        # Montar a query final
        query = f"""
        UPDATE CONTAS_CORRENTES SET
            {", ".join(campos)}
        WHERE ID = ?
        """
        
        # Adicionar o ID nos parâmetros
        params.append(id_conta)
        
        execute_query(query, tuple(params))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar conta corrente: {e}")
        raise Exception(f"Erro ao atualizar conta corrente: {str(e)}")

def excluir_conta_corrente(id_conta):
    """
    Exclui uma conta corrente do banco de dados
    
    Args:
        id_conta (int): ID da conta corrente a ser excluída
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se a conta existe
        conta = buscar_conta_corrente_por_id(id_conta)
        if not conta:
            raise Exception(f"Conta corrente com ID {id_conta} não encontrada")
        
        # Excluir a conta
        query = """
        DELETE FROM CONTAS_CORRENTES
        WHERE ID = ?
        """
        execute_query(query, (id_conta,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir conta corrente: {e}")
        raise Exception(f"Erro ao excluir conta corrente: {str(e)}")

def filtrar_contas_correntes(codigo="", descricao=""):
    """
    Filtra as contas correntes com base nos critérios informados
    
    Args:
        codigo (str, optional): Código da conta (filtro parcial)
        descricao (str, optional): Descrição da conta (filtro parcial)
        
    Returns:
        list: Lista de contas correntes filtradas
    """
    try:
        query = """
        SELECT ID, CODIGO, DESCRICAO, BANCO, BANCO_DESCRICAO, CAIXA_PDV
        FROM CONTAS_CORRENTES
        WHERE 1=1
        """
        
        params = []
        
        if codigo:
            query += " AND CODIGO LIKE ?"
            params.append(f"%{codigo}%")
        
        if descricao:
            query += " AND UPPER(DESCRICAO) LIKE UPPER(?)"
            params.append(f"%{descricao}%")
        
        query += " ORDER BY CODIGO"
        
        return execute_query(query, tuple(params) if params else None)
    except Exception as e:
        print(f"Erro ao filtrar contas correntes: {e}")
        raise Exception(f"Erro ao filtrar contas correntes: {str(e)}")

#Classes Financeiras 
def verificar_tabela_classes_financeiras():
    """
    Verifica se a tabela CLASSES_FINANCEIRAS existe e a cria se não existir
    
    Returns:
        bool: True se a tabela existe ou foi criada com sucesso
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'CLASSES_FINANCEIRAS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela CLASSES_FINANCEIRAS não encontrada. Criando...")
            query_create = """
            CREATE TABLE CLASSES_FINANCEIRAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                CODIGO VARCHAR(20) NOT NULL,
                DESCRICAO VARCHAR(100) NOT NULL,
                UNIQUE (CODIGO)
            )
            """
            execute_query(query_create)
            print("Tabela CLASSES_FINANCEIRAS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_CLASSES_FINANCEIRAS_ID
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
                CREATE TRIGGER CLASSES_FINANCEIRAS_BI FOR CLASSES_FINANCEIRAS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                    IF (NEW.ID IS NULL) THEN
                        NEW.ID = GEN_ID(GEN_CLASSES_FINANCEIRAS_ID, 1);
                    END
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Trigger pode já existir: {e}")
                # Se o trigger já existir, ignoramos o erro
                pass
            
            # Inserir dados iniciais
            dados_iniciais = [
                ("001", "DESPESAS OPERACIONAIS"),
                ("002", "DESPESAS ADMINISTRATIVAS"),
                ("003", "RECEITAS"),
                ("004", "INVESTIMENTOS")
            ]
            
            for dado in dados_iniciais:
                try:
                    query_insert = """
                    INSERT INTO CLASSES_FINANCEIRAS (CODIGO, DESCRICAO)
                    VALUES (?, ?)
                    """
                    execute_query(query_insert, dado)
                    print(f"Classe {dado[0]} inserida com sucesso.")
                except Exception as e:
                    print(f"Aviso: Erro ao inserir classe {dado[0]}: {e}")
            
            return True
        else:
            print("Tabela CLASSES_FINANCEIRAS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de classes financeiras: {str(e)}")

def listar_classes_financeiras():
    """
    Lista todas as classes financeiras cadastradas
    
    Returns:
        list: Lista de tuplas com dados das classes financeiras (ID, CODIGO, DESCRICAO)
    """
    try:
        query = """
        SELECT ID, CODIGO, DESCRICAO
        FROM CLASSES_FINANCEIRAS
        ORDER BY CODIGO
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar classes financeiras: {e}")
        raise Exception(f"Erro ao listar classes financeiras: {str(e)}")

def criar_classe_financeira(codigo, descricao):
    """
    Cria uma nova classe financeira no banco de dados
    
    Args:
        codigo (str): Código da classe financeira
        descricao (str): Descrição da classe financeira
        
    Returns:
        int: ID da classe financeira criada
    """
    try:
        # Verificar se já existe uma classe com o mesmo código
        query_check = """
        SELECT ID FROM CLASSES_FINANCEIRAS 
        WHERE CODIGO = ?
        """
        result = execute_query(query_check, (codigo,))
        
        if result and len(result) > 0:
            raise Exception(f"Já existe uma classe financeira com o código {codigo}")
        
        # Inserir a classe financeira - o ID será gerado automaticamente pelo trigger
        query_insert = """
        INSERT INTO CLASSES_FINANCEIRAS (CODIGO, DESCRICAO)
        VALUES (?, ?)
        """
        
        execute_query(query_insert, (codigo, descricao))
        
        # Obter o ID da classe inserida
        result = execute_query(query_check, (codigo,))
        if result and len(result) > 0:
            return result[0][0]
        
        return None
    except Exception as e:
        print(f"Erro ao criar classe financeira: {e}")
        raise Exception(f"Erro ao criar classe financeira: {str(e)}")
@functools.lru_cache(maxsize=512)
def buscar_classe_financeira_por_id(id_classe):
    """
    Busca uma classe financeira pelo ID
    
    Args:
        id_classe (int): ID da classe financeira
        
    Returns:
        tuple: Dados da classe financeira ou None se não encontrada
    """
    try:
        query = """
        SELECT ID, CODIGO, DESCRICAO
        FROM CLASSES_FINANCEIRAS
        WHERE ID = ?
        """
        result = execute_query(query, (id_classe,))
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar classe financeira: {e}")
        raise Exception(f"Erro ao buscar classe financeira: {str(e)}")

def atualizar_classe_financeira(id_classe, codigo, descricao):
    """
    Atualiza uma classe financeira existente
    
    Args:
        id_classe (int): ID da classe financeira a ser atualizada
        codigo (str): Novo código da classe financeira
        descricao (str): Nova descrição da classe financeira
        
    Returns:
        bool: True se a atualização foi bem-sucedida
    """
    try:
        # Verificar se a classe existe
        classe = buscar_classe_financeira_por_id(id_classe)
        if not classe:
            raise Exception(f"Classe financeira com ID {id_classe} não encontrada")
        
        # Verificar se o código sendo alterado já está em uso
        if codigo != classe[1]:  # Comparar com o código atual (índice 1)
            query_check = """
            SELECT ID FROM CLASSES_FINANCEIRAS 
            WHERE CODIGO = ? AND ID <> ?
            """
            result = execute_query(query_check, (codigo, id_classe))
            
            if result and len(result) > 0:
                raise Exception(f"Já existe outra classe financeira com o código {codigo}")
        
        # Atualizar a classe financeira
        query_update = """
        UPDATE CLASSES_FINANCEIRAS
        SET CODIGO = ?, DESCRICAO = ?
        WHERE ID = ?
        """
        
        execute_query(query_update, (codigo, descricao, id_classe))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar classe financeira: {e}")
        raise Exception(f"Erro ao atualizar classe financeira: {str(e)}")

def excluir_classe_financeira(id_classe):
    """
    Exclui uma classe financeira do banco de dados
    
    Args:
        id_classe (int): ID da classe financeira a ser excluída
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        # Verificar se a classe existe
        classe = buscar_classe_financeira_por_id(id_classe)
        if not classe:
            raise Exception(f"Classe financeira com ID {id_classe} não encontrada")
        
        # Excluir a classe
        query_delete = """
        DELETE FROM CLASSES_FINANCEIRAS
        WHERE ID = ?
        """
        execute_query(query_delete, (id_classe,))
        
        return True
    except Exception as e:
        print(f"Erro ao excluir classe financeira: {e}")
        raise Exception(f"Erro ao excluir classe financeira: {str(e)}")

#Impressora 
def verificar_tabela_configuracao_impressoras():
    """
    Verifica se a tabela CONFIGURACAO_IMPRESSORAS existe e a cria se não existir
    """
    try:
        # Verificar se a tabela existe
        query_check = """
        SELECT COUNT(*) FROM RDB$RELATIONS 
        WHERE RDB$RELATION_NAME = 'CONFIGURACAO_IMPRESSORAS'
        """
        result = execute_query(query_check)
        
        # Se a tabela não existe, cria
        if result[0][0] == 0:
            print("Tabela CONFIGURACAO_IMPRESSORAS não encontrada. Criando...")
            query_create = """
            CREATE TABLE CONFIGURACAO_IMPRESSORAS (
                ID INTEGER NOT NULL PRIMARY KEY,
                CATEGORIA VARCHAR(50) NOT NULL,
                IMPRESSORA VARCHAR(100) NOT NULL,
                ESTACAO VARCHAR(50),
                DATA_CONFIGURACAO DATE,
                ID_USUARIO INTEGER,
                USUARIO VARCHAR(50)
            )
            """
            execute_query(query_create)
            print("Tabela CONFIGURACAO_IMPRESSORAS criada com sucesso.")
            
            # Criar o gerador de IDs (sequence)
            try:
                query_generator = """
                CREATE GENERATOR GEN_CONFIG_IMPRESSORAS_ID
                """
                execute_query(query_generator)
                print("Gerador de IDs criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Gerador pode já existir: {e}")
            
            # Criar o trigger com sintaxe mais simples
            try:
                query_trigger = """
                CREATE TRIGGER CONFIGURACAO_IMPRESSORAS_BI FOR CONFIGURACAO_IMPRESSORAS
                ACTIVE BEFORE INSERT POSITION 0
                AS
                BEGIN
                  NEW.ID = GEN_ID(GEN_CONFIG_IMPRESSORAS_ID, 1);
                END
                """
                execute_query(query_trigger)
                print("Trigger criado com sucesso.")
            except Exception as e:
                print(f"Aviso: Não foi possível criar o trigger: {e}")
            
            return True
        else:
            print("Tabela CONFIGURACAO_IMPRESSORAS já existe.")
        
        return True
    except Exception as e:
        print(f"Erro ao verificar/criar tabela: {e}")
        raise Exception(f"Erro ao verificar/criar tabela de configuração de impressoras: {str(e)}")

def salvar_configuracao_impressora(categoria, impressora, estacao=None):
    """
    Salva ou atualiza uma configuração de impressora
    
    Args:
        categoria (str): Categoria da impressora (ex: Padrão, Orçamento, etc.)
        impressora (str): Nome da impressora
        estacao (str, optional): Nome da estação
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        # Verificar se já existe uma configuração para esta categoria
        query_check = """
        SELECT ID FROM CONFIGURACAO_IMPRESSORAS 
        WHERE CATEGORIA = ?
        """
        result = execute_query(query_check, (categoria,))
        
        # Obter dados do usuário logado
        from datetime import date
        data_atual = date.today()
        id_usuario = None
        nome_usuario = None
        
        # Se houver um usuário logado, usar seus dados
        try:
            usuario_logado = get_usuario_logado()
            if usuario_logado and usuario_logado["id"]:
                id_usuario = usuario_logado["id"]
                nome_usuario = usuario_logado["nome"]
        except:
            pass  # Continua mesmo se não conseguir obter usuário logado
        
        # Se já existe, atualiza
        if result and len(result) > 0:
            id_config = result[0][0]
            
            query_update = """
            UPDATE CONFIGURACAO_IMPRESSORAS
            SET IMPRESSORA = ?, ESTACAO = ?, DATA_CONFIGURACAO = ?, ID_USUARIO = ?, USUARIO = ?
            WHERE ID = ?
            """
            
            execute_query(query_update, (
                impressora, estacao, data_atual, id_usuario, nome_usuario, id_config
            ))
        else:
            # Se não existe, insere
            query_insert = """
            INSERT INTO CONFIGURACAO_IMPRESSORAS (
                CATEGORIA, IMPRESSORA, ESTACAO, DATA_CONFIGURACAO, ID_USUARIO, USUARIO
            ) VALUES (?, ?, ?, ?, ?, ?)
            """
            
            execute_query(query_insert, (
                categoria, impressora, estacao, data_atual, id_usuario, nome_usuario
            ))
        
        print(f"Configuração de impressora para {categoria} salva com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao salvar configuração de impressora: {e}")
        raise Exception(f"Erro ao salvar configuração de impressora: {str(e)}")

def buscar_impressora_por_categoria(categoria):
    """
    Busca uma configuração de impressora pela categoria
    
    Args:
        categoria (str): Categoria da impressora
        
    Returns:
        str: Nome da impressora ou None se não encontrada
    """
    try:
        query = """
        SELECT IMPRESSORA FROM CONFIGURACAO_IMPRESSORAS
        WHERE CATEGORIA = ?
        """
        result = execute_query(query, (categoria,))
        
        if result and len(result) > 0:
            return result[0][0]
        return None
    except Exception as e:
        print(f"Erro ao buscar impressora por categoria: {e}")
        return None

def listar_configuracoes_impressoras():
    """
    Lista todas as configurações de impressoras
    
    Returns:
        list: Lista de tuplas com dados das configurações (ID, CATEGORIA, IMPRESSORA, ESTACAO)
    """
    try:
        query = """
        SELECT ID, CATEGORIA, IMPRESSORA, ESTACAO
        FROM CONFIGURACAO_IMPRESSORAS
        ORDER BY CATEGORIA
        """
        return execute_query(query)
    except Exception as e:
        print(f"Erro ao listar configurações de impressoras: {e}")
        raise Exception(f"Erro ao listar configurações de impressoras: {str(e)}")

def excluir_configuracao_impressora(id_config):
    """
    Exclui uma configuração de impressora
    
    Args:
        id_config (int): ID da configuração
        
    Returns:
        bool: True se a exclusão foi bem-sucedida
    """
    try:
        query = """
        DELETE FROM CONFIGURACAO_IMPRESSORAS
        WHERE ID = ?
        """
        execute_query(query, (id_config,))
        return True
    except Exception as e:
        print(f"Erro ao excluir configuração de impressora: {e}")
        raise Exception(f"Erro ao excluir configuração de impressora: {str(e)}")

# cadastrar funcionario para login
def verificar_usuario_existente(nome_usuario):
    """
    Verifica se já existe um usuário com o nome especificado
    
    Args:
        nome_usuario (str): Nome de usuário a verificar
        
    Returns:
        bool: True se o usuário já existe, False caso contrário
    """
    try:
        query = """
        SELECT COUNT(*) FROM USUARIOS
        WHERE USUARIO = ?
        """
        result = execute_query(query, (nome_usuario,))
        
        if result and result[0][0] > 0:
            return True
        return False
    except Exception as e:
        print(f"Erro ao verificar usuário: {e}")
        raise Exception(f"Erro ao verificar usuário: {str(e)}")

def vincular_usuario_funcionario(id_funcionario, id_usuario, nome_usuario):
    """
    Vincula um usuário a um funcionário
    
    Args:
        id_funcionario (int): ID do funcionário
        id_usuario (int): ID do usuário
        nome_usuario (str): Nome de usuário (para facilitar consultas)
        
    Returns:
        bool: True se a operação foi bem-sucedida
    """
    try:
        query = """
        UPDATE FUNCIONARIOS
        SET ID_USUARIO = ?, NOME_USUARIO = ?
        WHERE ID = ?
        """
        execute_query(query, (id_usuario, nome_usuario, id_funcionario))
        return True
    except Exception as e:
        print(f"Erro ao vincular usuário a funcionário: {e}")
        raise Exception(f"Erro ao vincular usuário a funcionário: {str(e)}")

def verificar_tabela_funcionarios_atualizacao():
    """
    Verifica se a tabela FUNCIONARIOS tem as colunas necessárias 
    para vincular usuários e as adiciona se necessário
    
    Returns:
        bool: True se a tabela está pronta ou foi atualizada com sucesso
    """
    try:
        # Verificar se a coluna ID_USUARIO existe
        query_check_id = """
        SELECT COUNT(*) FROM RDB$RELATION_FIELDS 
        WHERE RDB$RELATION_NAME = 'FUNCIONARIOS' 
        AND RDB$FIELD_NAME = 'ID_USUARIO'
        """
        result_id = execute_query(query_check_id)
        
        # Verificar se a coluna NOME_USUARIO existe
        query_check_nome = """
        SELECT COUNT(*) FROM RDB$RELATION_FIELDS 
        WHERE RDB$RELATION_NAME = 'FUNCIONARIOS' 
        AND RDB$FIELD_NAME = 'NOME_USUARIO'
        """
        result_nome = execute_query(query_check_nome)
        
        # Se as colunas não existem, adicioná-las
        if result_id[0][0] == 0:
            query_add_id = """
            ALTER TABLE FUNCIONARIOS
            ADD ID_USUARIO INTEGER
            """
            execute_query(query_add_id)
            print("Coluna ID_USUARIO adicionada à tabela FUNCIONARIOS")
        
        if result_nome[0][0] == 0:
            query_add_nome = """
            ALTER TABLE FUNCIONARIOS
            ADD NOME_USUARIO VARCHAR(50)
            """
            execute_query(query_add_nome)
            print("Coluna NOME_USUARIO adicionada à tabela FUNCIONARIOS")
            
        # Adicionar chave estrangeira se ambas as colunas foram adicionadas
        if result_id[0][0] == 0 and result_nome[0][0] == 0:
            # Verificar se a chave estrangeira já existe
            try:
                query_add_fk = """
                ALTER TABLE FUNCIONARIOS ADD CONSTRAINT FK_FUNCIONARIO_USUARIO
                FOREIGN KEY (ID_USUARIO) REFERENCES USUARIOS(ID)
                ON DELETE SET NULL
                """
                execute_query(query_add_fk)
                print("Chave estrangeira FK_FUNCIONARIO_USUARIO adicionada")
            except Exception as e:
                # Ignorar se a chave já existir
                print(f"Nota: {e}")
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar tabela FUNCIONARIOS: {e}")
        return False

def autenticar_por_funcionario(nome_usuario, senha):
    """
    Autentica um usuário e recupera informações do funcionário vinculado
    
    Args:
        nome_usuario (str): Nome de usuário
        senha (str): Senha do usuário
        
    Returns:
        dict: Informações do funcionário e usuário ou None se autenticação falhar
    """
    try:
        # Verificar credenciais na tabela USUARIOS
        query_auth = """
        SELECT U.ID, U.USUARIO, U.EMPRESA, F.ID, F.NOME
        FROM USUARIOS U
        LEFT JOIN FUNCIONARIOS F ON F.ID_USUARIO = U.ID
        WHERE U.USUARIO = ? AND U.SENHA = ?
        """
        result = execute_query(query_auth, (nome_usuario, senha))
        
        if result and len(result) > 0:
            # Usuário autenticado
            user_info = {
                "id_usuario": result[0][0],
                "usuario": result[0][1],
                "empresa": result[0][2],
                "id_funcionario": result[0][3],
                "nome_funcionario": result[0][4]
            }
            return user_info
        
        return None
    except Exception as e:
        print(f"Erro na autenticação por funcionário: {e}")
        return None


def criar_usuario(usuario, senha, empresa, usuario_master=None, data_expiracao=None, acesso_ecommerce='N'):
    """
    Cria um novo usuário no banco de dados, incluindo a permissão de e-commerce.
    
    Args:
        usuario (str): Nome de usuário
        senha (str): Senha do usuário (IMPORTANTE: o código original não fazia hash,
                     isso deve ser considerado por segurança)
        empresa (str): Nome da empresa
        usuario_master (int, optional): ID do usuário master/principal
        data_expiracao (date, optional): Data de expiração do acesso
        acesso_ecommerce (str, optional): 'S' para sim, 'N' para não.
    
    Returns:
        int: ID do usuário criado ou None em caso de erro
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
        
        # --- ALTERAÇÃO PRINCIPAL AQUI ---
        # Adicionamos a coluna ACESSO_ECOMMERCE na query de inserção
        query_insert = """
        INSERT INTO USUARIOS (
            ID, USUARIO, SENHA, EMPRESA, BLOQUEADO, USUARIO_MASTER, DATA_EXPIRACAO, ACESSO_ECOMMERCE
        ) VALUES (?, ?, ?, ?, 'N', ?, ?, ?)
        """
        # Adicionamos o parâmetro 'acesso_ecommerce' no final da tupla
        execute_query(query_insert, (next_id, usuario, senha, empresa, usuario_master, data_expiracao, acesso_ecommerce))
        
        return next_id
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        raise Exception(f"Erro ao criar usuário: {str(e)}")



def modificar_acesso_ecommerce(usuario_master_id, novo_status):
    """
    Modifica o status de acesso ao e-commerce para um usuário master e todos os seus funcionários.
    Args:
        usuario_master_id: ID do usuário master.
        novo_status: 'S' para liberar, 'N' para bloquear.
    """
    if novo_status not in ['S', 'N']:
        raise ValueError("Status inválido. Use 'S' ou 'N'.")

    # Atualiza tanto o usuário master quanto todos os funcionários vinculados a ele
    query = "UPDATE USUARIOS SET ACESSO_ECOMMERCE = ? WHERE ID = ? OR USUARIO_MASTER = ?"
    params = (novo_status, usuario_master_id, usuario_master_id)
    
    execute_query(query, params, commit=True)
    print(f"Acesso e-commerce para o usuário master {usuario_master_id} e seus funcionários foi definido como '{novo_status}'.")


def verificar_acesso_ecommerce(usuario_id):
    """
    Verifica se a conta do usuário (ou de seu master) tem acesso ao e-commerce.
    Retorna True se tiver acesso, False caso contrário.
    """
    if not usuario_id:
        return False

    conn = get_connection()
    cur = conn.cursor()

    # Primeiro, verifica o próprio usuário
    cur.execute("SELECT ACESSO_ECOMMERCE, USUARIO_MASTER FROM USUARIOS WHERE ID = ?", (usuario_id,))
    resultado = cur.fetchone()

    if not resultado:
        conn.close()
        return False

    acesso, master_id = resultado
    
    # Se o próprio usuário tem a flag 'S', ele tem acesso (caso do master)
    if acesso and acesso.strip() == 'S':
        conn.close()
        return True
    
    # Se ele é um funcionário (tem um master_id), verifica o acesso do master
    if master_id is not None:
        cur.execute("SELECT ACESSO_ECOMMERCE FROM USUARIOS WHERE ID = ?", (master_id,))
        resultado_master = cur.fetchone()
        conn.close()
        if resultado_master and resultado_master[0] and resultado_master[0].strip() == 'S':
            return True

    conn.close()
    return False
    
def buscar_funcionario_por_usuario(nome_usuario):
    """
    Busca um funcionário pelo nome de usuário
    
    Args:
        nome_usuario (str): Nome de usuário
        
    Returns:
        tuple: (id_funcionario, nome_funcionario) ou None se não encontrado
    """
    try:
        query = """
        SELECT F.ID, F.NOME 
        FROM FUNCIONARIOS F
        WHERE F.NOME_USUARIO = ?
        """
        result = execute_query(query, (nome_usuario,))
        
        if result and len(result) > 0:
            return result[0]
        return None
    except Exception as e:
        print(f"Erro ao buscar funcionário por usuário: {e}")
        return None

#Vendas
def verificar_tabela_vendas(self):
    """Verifica a estrutura da tabela VENDAS"""
    try:
        from base.banco import execute_query
        
        # Verificar se a tabela existe
        result = execute_query("SELECT COUNT(*) FROM RDB$RELATIONS WHERE RDB$RELATION_NAME = 'VENDAS'")
        tabela_existe = result[0][0] > 0
        print(f"Tabela VENDAS existe: {tabela_existe}")
        
        if tabela_existe:
            # Verificar estrutura
            colunas = execute_query("SELECT RDB$FIELD_NAME FROM RDB$RELATION_FIELDS WHERE RDB$RELATION_NAME = 'VENDAS'")
            print("Colunas da tabela VENDAS:")
            for col in colunas: 
                print(f"- {col[0].strip()}")
                
            # Verificar quantidade de registros
            count = execute_query("SELECT COUNT(*) FROM VENDAS")
            print(f"Total de registros: {count[0][0]}")
            
            # Mostrar amostra de dados
            amostra = execute_query("SELECT ID_VENDA, VALOR_TOTAL FROM VENDAS LIMIT 5")
            print("Amostra de dados:")
            for reg in amostra:
                print(f"ID: {reg[0]}, VALOR_TOTAL: {reg[1]}")
                
        return tabela_existe
    except Exception as e:
        print(f"Erro ao verificar tabela VENDAS: {e}")
        return False

#Lancamento
def registrar_pagamento(self, recebimento_id, valor_pago):
    """
    Registra um pagamento (total ou parcial) de uma parcela
    
    Args:
        recebimento_id: ID do recebimento/parcela
        valor_pago: Valor que está sendo pago agora
    """
    import sqlite3
    from datetime import date
    
    # Conectar ao banco de dados
    conn = sqlite3.connect('base/banco_sistema.db')
    cursor = conn.cursor()
    
    try:
        # Buscar informações atuais da parcela
        cursor.execute("""
            SELECT VALOR, VALOR_ORIGINAL, STATUS
            FROM RECEBIMENTOS_CLIENTES
            WHERE ID = ?
        """, (recebimento_id,))
        
        resultado = cursor.fetchone()
        if not resultado:
            raise Exception(f"Recebimento ID {recebimento_id} não encontrado")
        
        valor_pendente, valor_original, status_atual = resultado
        
        # Validar valor do pagamento
        if valor_pago <= 0:
            raise Exception("O valor do pagamento deve ser maior que zero")
            
        if valor_pago > valor_pendente:
            raise Exception(f"O valor do pagamento (R$ {valor_pago:.2f}) excede o valor pendente (R$ {valor_pendente:.2f})")
        
        # Calcular novo valor pendente
        novo_valor_pendente = valor_pendente - valor_pago
        
        # Determinar novo status
        if novo_valor_pendente == 0:
            novo_status = "PAGO"
        else:
            novo_status = "PARCIAL"
        
        # Registrar a data do pagamento apenas se for pagamento total
        data_recebimento = None
        if novo_status == "PAGO":
            data_recebimento = date.today()
        
        # Atualizar a parcela
        cursor.execute("""
            UPDATE RECEBIMENTOS_CLIENTES
            SET VALOR = ?,
                STATUS = ?,
                DATA_RECEBIMENTO = ?
            WHERE ID = ?
        """, (novo_valor_pendente, novo_status, data_recebimento, recebimento_id))
        
        conn.commit()
        
        # Registrar este pagamento no log ou histórico se desejar
        # Esta parte é opcional, mas útil para manter um histórico de pagamentos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS HISTORICO_PAGAMENTOS (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                RECEBIMENTO_ID INTEGER,
                DATA_PAGAMENTO DATE,
                VALOR_PAGO DECIMAL(10,2),
                OBSERVACAO TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO HISTORICO_PAGAMENTOS (
                RECEBIMENTO_ID, DATA_PAGAMENTO, VALOR_PAGO, OBSERVACAO
            ) VALUES (?, ?, ?, ?)
        """, (recebimento_id, date.today(), valor_pago, f"Pagamento {'total' if novo_status == 'PAGO' else 'parcial'}"))
        
        conn.commit()
        
        return True, f"Pagamento de R$ {valor_pago:.2f} registrado com sucesso. Status: {novo_status}"
        
    except Exception as e:
        conn.rollback()
        return False, f"Erro ao registrar pagamento: {str(e)}"
        
    finally:
        conn.close()

def listar_recebimentos_baixados():
    """
    Lista todos os recebimentos com status 'Recebido'
    
    Returns:
        list: Lista de tuplas com os dados dos recebimentos baixados
    """
    try:
        print("Buscando recebimentos com status 'Recebido'...")
        
        # Use a função execute_query existente no banco.py em vez de SQLite
        query = """
        SELECT ID, CODIGO, CLIENTE, CLIENTE_ID, VENCIMENTO, VALOR, DATA_RECEBIMENTO, STATUS, VALOR_ORIGINAL
        FROM RECEBIMENTOS_CLIENTES
        WHERE STATUS = 'Recebido'
        ORDER BY DATA_RECEBIMENTO DESC
        """
        result = execute_query(query)
        
        # Informar no log quantos registros foram encontrados para debug
        print(f"Encontrados {len(result) if result else 0} recebimentos com status 'Recebido'")
        
        # Verificar se há registros para debug
        if result and len(result) > 0:
            print(f"Primeiro registro encontrado: {result[0]}")
        
        return result
    except Exception as e:
        print(f"Erro ao listar recebimentos baixados: {e}")
        import traceback
        traceback.print_exc()
        return []

def buscar_historico_pagamentos(codigo):
    """
    Busca o histórico de pagamentos de um determinado código
    
    Args:
        codigo (str): Código do recebimento
        
    Returns:
        list: Lista de tuplas (data_pagamento, valor_pago, observacao)
    """
    import sqlite3
    from datetime import datetime
    
    # Use get_db_path para obter o caminho correto
    banco_path = get_db_path()
    conn = sqlite3.connect(banco_path)
    cursor = conn.cursor()
    
    try:
        # Primeiro, buscar o ID do recebimento pelo código
        cursor.execute("SELECT ID FROM RECEBIMENTOS_CLIENTES WHERE CODIGO = ?", (codigo,))
        resultado = cursor.fetchone()
        
        if not resultado:
            return []
        
        recebimento_id = resultado[0]
        
        # Verifica se a tabela HISTORICO_PAGAMENTOS existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='HISTORICO_PAGAMENTOS'
        """)
        if not cursor.fetchone():
            # Se a tabela não existir, cria ela
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS HISTORICO_PAGAMENTOS (
                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    RECEBIMENTO_ID INTEGER,
                    DATA_PAGAMENTO DATE,
                    VALOR_PAGO DECIMAL(10,2),
                    OBSERVACAO TEXT
                )
            """)
            conn.commit()
            # Como a tabela acabou de ser criada, não há histórico
            return []
        
        # Agora, buscar o histórico de pagamentos
        cursor.execute("""
            SELECT DATA_PAGAMENTO, VALOR_PAGO, OBSERVACAO
            FROM HISTORICO_PAGAMENTOS
            WHERE RECEBIMENTO_ID = ?
            ORDER BY DATA_PAGAMENTO DESC
        """, (recebimento_id,))
        
        historico = []
        
        # Converter strings de data para objetos date
        for row in cursor.fetchall():
            data_pagamento_str, valor_pago, observacao = row
            
            # Converter string de data de pagamento para date
            data_pagamento = None
            if data_pagamento_str:
                try:
                    if isinstance(data_pagamento_str, str):
                        # Se for string, tenta converter para date
                        data_pagamento = datetime.strptime(data_pagamento_str, '%Y-%m-%d').date()
                    else:
                        # Se não for string, assume que já é um objeto date
                        data_pagamento = data_pagamento_str
                except:
                    pass
            
            historico.append((data_pagamento, valor_pago, observacao))
        
        # Se não houver histórico na tabela de histórico, criar um registro baseado no próprio recebimento
        if not historico:
            # Buscar as informações do recebimento
            cursor.execute("""
                SELECT DATA_RECEBIMENTO, VALOR_ORIGINAL - VALOR, 'Pagamento total'
                FROM RECEBIMENTOS_CLIENTES
                WHERE ID = ? AND STATUS = 'Recebido'
            """, (recebimento_id,))
            
            result = cursor.fetchone()
            if result:
                data_recebimento_str, valor_pago, observacao = result
                
                # Converter string de data de recebimento para date
                data_recebimento = None
                if data_recebimento_str:
                    try:
                        if isinstance(data_recebimento_str, str):
                            # Se for string, tenta converter para date
                            data_recebimento = datetime.strptime(data_recebimento_str, '%Y-%m-%d').date()
                        else:
                            # Se não for string, assume que já é um objeto date
                            data_recebimento = data_recebimento_str
                    except:
                        pass
                
                # Adicionar ao histórico
                historico.append((data_recebimento, valor_pago, observacao))
        
        return historico
    
    except Exception as e:
        print(f"Erro ao buscar histórico de pagamentos: {e}")
        return []
    
    finally:
        conn.close()

def iniciar_sincronizacao():
    """Inicia o sistema de sincronização"""
    try:
        t = threading.Thread(target=monitor_sincronizacao, daemon=True)
        t.start()
        print("Sistema de sincronização iniciado")
        
        # Registrar função para ser executada no encerramento do programa
        atexit.register(sincronizar_ao_encerrar)
    except Exception as e:
        print(f"Erro ao iniciar sistema de sincronização: {e}")

# Adicionar à lista de inicialização no final do arquivo
if __name__ == "__main__":
    try:
        print(f"Iniciando configuração do banco de dados: {DB_PATH}")
        # Suas funções de verificação de tabelas...
        print("Banco de dados inicializado com sucesso!")
        
        # Adicione esta linha:
        iniciar_sincronizacao()
        
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {str(e)}")
