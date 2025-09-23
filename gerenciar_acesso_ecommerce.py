#!/usr/bin/env python3
"""
Utilitário para gerenciar o acesso ao módulo E-commerce (Mercado Livre)
Permite aos administradores conceder ou bloquear acesso aos usuários
"""

import sys
import os
from base.banco import (
    listar_usuarios, 
    alterar_acesso_ecommerce, 
    listar_usuarios_sem_acesso_ecommerce,
    verificar_acesso_ecommerce,
    execute_query
)

def listar_todos_usuarios_com_status():
    """Lista todos os usuários com seu status de acesso ao e-commerce"""
    try:
        query = """
        SELECT ID, USUARIO, EMPRESA, 
               COALESCE(ACESSO_ECOMMERCE, 'S') as ACESSO_ECOMMERCE
        FROM USUARIOS
        ORDER BY EMPRESA, USUARIO
        """
        usuarios = execute_query(query)
        
        print("\n=== USUÁRIOS E STATUS DE ACESSO AO E-COMMERCE ===")
        print(f"{'ID':<5} {'USUÁRIO':<20} {'EMPRESA':<20} {'ACESSO':<8}")
        print("-" * 60)
        
        for usuario in usuarios:
            id_user, nome, empresa, acesso = usuario
            status = "✅ SIM" if acesso == 'S' else "❌ NÃO"
            print(f"{id_user:<5} {nome:<20} {empresa:<20} {status:<8}")
            
        return usuarios
        
    except Exception as e:
        print(f"Erro ao listar usuários: {e}")
        return []

def bloquear_usuario():
    """Interface para bloquear acesso de um usuário"""
    print("\n=== BLOQUEAR ACESSO AO E-COMMERCE ===")
    
    try:
        usuario_id = int(input("Digite o ID do usuário para bloquear: "))
        
        # Verificar se o usuário existe
        query = "SELECT USUARIO, EMPRESA FROM USUARIOS WHERE ID = ?"
        result = execute_query(query, (usuario_id,))
        
        if not result:
            print("❌ Usuário não encontrado!")
            return
            
        nome, empresa = result[0]
        print(f"Usuário encontrado: {nome} (Empresa: {empresa})")
        
        confirmacao = input("Confirma o bloqueio? (s/N): ").lower()
        if confirmacao == 's':
            if alterar_acesso_ecommerce(usuario_id, False):
                print(f"✅ Acesso ao e-commerce bloqueado para {nome}")
            else:
                print("❌ Erro ao bloquear acesso")
        else:
            print("Operação cancelada")
            
    except ValueError:
        print("❌ ID inválido. Digite apenas números.")
    except Exception as e:
        print(f"❌ Erro: {e}")

def conceder_acesso():
    """Interface para conceder acesso a um usuário"""
    print("\n=== CONCEDER ACESSO AO E-COMMERCE ===")
    
    try:
        usuario_id = int(input("Digite o ID do usuário para conceder acesso: "))
        
        # Verificar se o usuário existe
        query = "SELECT USUARIO, EMPRESA FROM USUARIOS WHERE ID = ?"
        result = execute_query(query, (usuario_id,))
        
        if not result:
            print("❌ Usuário não encontrado!")
            return
            
        nome, empresa = result[0]
        print(f"Usuário encontrado: {nome} (Empresa: {empresa})")
        
        confirmacao = input("Confirma a concessão de acesso? (s/N): ").lower()
        if confirmacao == 's':
            if alterar_acesso_ecommerce(usuario_id, True):
                print(f"✅ Acesso ao e-commerce concedido para {nome}")
            else:
                print("❌ Erro ao conceder acesso")
        else:
            print("Operação cancelada")
            
    except ValueError:
        print("❌ ID inválido. Digite apenas números.")
    except Exception as e:
        print(f"❌ Erro: {e}")

def testar_acesso():
    """Interface para testar acesso de um usuário"""
    print("\n=== TESTAR ACESSO AO E-COMMERCE ===")
    
    usuario = input("Digite o nome do usuário: ").strip()
    empresa = input("Digite a empresa (ou Enter para pular): ").strip()
    
    if not empresa:
        empresa = None
        
    try:
        tem_acesso, motivo = verificar_acesso_ecommerce(usuario, empresa)
        
        print(f"\nUsuário: {usuario}")
        if empresa:
            print(f"Empresa: {empresa}")
            
        if tem_acesso:
            print("✅ ACESSO CONCEDIDO - Usuário pode acessar o módulo Mercado Livre")
        else:
            print(f"❌ ACESSO NEGADO - {motivo}")
            
    except Exception as e:
        print(f"❌ Erro ao testar acesso: {e}")

def menu_principal():
    """Menu principal do utilitário"""
    while True:
        print("\n" + "="*50)
        print("  GERENCIADOR DE ACESSO AO E-COMMERCE")
        print("="*50)
        print("1. Listar todos os usuários com status")
        print("2. Bloquear acesso de um usuário")
        print("3. Conceder acesso a um usuário")
        print("4. Testar acesso de um usuário")
        print("5. Listar apenas usuários bloqueados")
        print("0. Sair")
        print("-"*50)
        
        try:
            opcao = input("Escolha uma opção: ").strip()
            
            if opcao == '1':
                listar_todos_usuarios_com_status()
            elif opcao == '2':
                bloquear_usuario()
            elif opcao == '3':
                conceder_acesso()
            elif opcao == '4':
                testar_acesso()
            elif opcao == '5':
                usuarios_bloqueados = listar_usuarios_sem_acesso_ecommerce()
                if usuarios_bloqueados:
                    print("\n=== USUÁRIOS BLOQUEADOS ===")
                    for usuario in usuarios_bloqueados:
                        print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Empresa: {usuario[2]}")
                else:
                    print("✅ Nenhum usuário está bloqueado no momento")
            elif opcao == '0':
                print("👋 Saindo...")
                break
            else:
                print("❌ Opção inválida!")
                
        except KeyboardInterrupt:
            print("\n👋 Saindo...")
            break
        except Exception as e:
            print(f"❌ Erro: {e}")

if __name__ == "__main__":
    print("🔐 Utilitário de Gerenciamento de Acesso ao E-commerce")
    print("⚠️  Execute este script apenas se você tem acesso administrativo ao banco de dados")
    
    try:
        # Verificar se consegue conectar ao banco
        usuarios = listar_usuarios()
        if not usuarios:
            print("⚠️  Nenhum usuário encontrado ou erro na conexão com o banco")
        
        menu_principal()
        
    except Exception as e:
        print(f"❌ Erro fatal: {e}")
        print("💡 Certifique-se de que:")
        print("   - O banco de dados está acessível")
        print("   - Você tem permissões adequadas")
        print("   - As tabelas do sistema foram criadas")
        sys.exit(1)