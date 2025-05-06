"""
Script para inicializar o banco de dados - execute-o antes de usar o sistema
"""
import os
import sys
import time
from base.banco import verificar_tabela_usuarios, criar_usuario_padrao, listar_usuarios, get_db_path, get_connection

def inicializar_banco():
    """Inicializa o banco de dados"""
    print("\n===== INICIALIZAÇÃO DO BANCO DE DADOS =====\n")
    
    # Mostrar onde está procurando o banco
    db_path = get_db_path()
    print(f"Arquivo de banco de dados: {db_path}")
    
    # Verificar se o diretório existe
    db_dir = os.path.dirname(db_path)
    if not os.path.exists(db_dir):
        print(f"Diretório não encontrado: {db_dir}")
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"Diretório criado: {db_dir}")
        except Exception as e:
            print(f"ERRO: Não foi possível criar o diretório: {e}")
    
    # Tentar conectar ao banco
    try:
        print("\nTentando conectar ao banco de dados...")
        conn = get_connection()
        print("Conexão estabelecida com sucesso!")
        conn.close()
        print("Conexão fechada.")
    except Exception as e:
        print(f"ERRO de conexão: {e}")
        print("\nVerifique se:")
        print("1. O servidor Firebird está instalado e em execução")
        print("2. O arquivo do banco existe no caminho correto")
        print("3. As credenciais (usuário/senha) estão corretas")
        print("\nPressione ENTER para sair...")
        input()
        return False
    
    # Verificar/criar tabela de usuários
    try:
        print("\nVerificando tabela de usuários...")
        verificar_tabela_usuarios()
        print("Verificação de tabela concluída.")
    except Exception as e:
        print(f"\nERRO ao verificar/criar tabela: {e}")
        print("\nPressione ENTER para sair...")
        input()
        return False
    
    # Criar usuário padrão se necessário
    try:
        print("\nVerificando usuário padrão...")
        criar_usuario_padrao()
        print("Verificação de usuário padrão concluída.")
    except Exception as e:
        print(f"\nERRO ao criar usuário padrão: {e}")
        print("\nPressione ENTER para sair...")
        input()
        return False
    
    # Listar usuários
    try:
        print("\nListando usuários cadastrados:")
        usuarios = listar_usuarios()
        if not usuarios:
            print("Nenhum usuário encontrado!")
        else:
            for usuario in usuarios:
                print(f"ID: {usuario[0]}, Usuário: {usuario[1]}, Empresa: {usuario[2]}")
    except Exception as e:
        print(f"\nERRO ao listar usuários: {e}")
    
    print("\nInicialização do banco de dados concluída com sucesso!")
    print("\nVocê pode agora executar o sistema normalmente.")
    print("\nPressione ENTER para sair...")
    input()
    return True

if __name__ == "__main__":
    inicializar_banco()