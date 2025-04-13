"""
Script para testar a conexão com o banco de dados
"""
import os
from base.banco import get_connection, verificar_tabela_usuarios, criar_usuario_padrao

def testar_conexao():
    print("\n===== TESTE DE CONEXÃO COM O BANCO =====\n")
    
    try:
        # Tentar obter uma conexão
        conn = get_connection()
        print("Conexão com o banco estabelecida com sucesso!")
        
        # Fechar conexão
        conn.close()
        print("Conexão fechada com sucesso!")
        
        # Verificar/criar tabela de usuários
        print("\nVerificando tabela de usuários...")
        verificar_tabela_usuarios()
        print("Tabela de usuários verificada/criada com sucesso!")
        
        # Criar usuário padrão se não existir
        print("\nVerificando usuário padrão...")
        criar_usuario_padrao()
        print("Usuário padrão verificado/criado com sucesso!")
        
        print("\nTodos os testes de banco de dados foram bem-sucedidos!")
        
    except Exception as e:
        print(f"\nERRO: {e}")
    
    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    testar_conexao()