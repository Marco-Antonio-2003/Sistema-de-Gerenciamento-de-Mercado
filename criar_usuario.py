"""
Script para criar usuários diretamente no banco de dados
Execute este script quando precisar adicionar novos usuários
"""
import sys
import os
from base.banco import criar_usuario, verificar_tabela_usuarios

def main():
    print("\n===== CADASTRO DE USUÁRIOS =====\n")
    
    # Verificar se a tabela de usuários existe
    try:
        verificar_tabela_usuarios()
    except Exception as e:
        print(f"Erro ao verificar tabela de usuários: {e}")
        input("\nPressione ENTER para sair...")
        return
    
    # Solicitar informações do usuário
    usuario = input("Digite o nome de usuário: ").strip()
    senha = input("Digite a senha: ").strip()
    empresa = input("Digite o nome da empresa: ").strip()
    
    # Validar campos
    if not usuario or not senha or not empresa:
        print("\nTodos os campos são obrigatórios!")
        input("\nPressione ENTER para sair...")
        return
    
    # Confirmar
    print("\nConfirme os dados:")
    print(f"Usuário: {usuario}")
    print(f"Senha: {'*' * len(senha)}")
    print(f"Empresa: {empresa}")
    
    confirma = input("\nConfirmar cadastro? (S/N): ").strip().upper()
    
    if confirma != 'S':
        print("\nOperação cancelada!")
        input("\nPressione ENTER para sair...")
        return
    
    # Criar usuário
    try:
        criar_usuario(usuario, senha, empresa)
        print("\nUsuário criado com sucesso!")
    except Exception as e:
        print(f"\nErro ao criar usuário: {e}")
    
    input("\nPressione ENTER para sair...")

if __name__ == "__main__":
    main()