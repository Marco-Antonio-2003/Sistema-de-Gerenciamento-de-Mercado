# atualizador.py - VERSÃO CORRIGIDA COM DEBUG
import os
import sys
import requests
import subprocess
import tempfile
import time
# Obter versão atual do sistema dinamicamente
try:
    from login import Versao
    # Extrai a versão do formato "Versão: v0.1.5.3"
    VERSAO_ATUAL = Versao.split(": ")[1].strip() if ": " in Versao else "v0.1.0.0"
except ImportError:
    VERSAO_ATUAL = "v0.1.0.0"

REPO_API = "https://api.github.com/repos/Marco-Antonio-2003/Sistema-de-Gerenciamento-de-Mercado/releases/latest"

def comparar_versoes(versao1, versao2):
    """
    Compara duas versões no formato vX.Y.Z.W (ou vX.Y.Z)
    Retorna 1 se versao1 > versao2, -1 se versao1 < versao2, 0 se iguais
    """
    try:
        # Remove o 'v' inicial, espaços e divide pelos pontos
        v1_str = versao1.strip().lstrip('v')
        v2_str = versao2.strip().lstrip('v')
        
        print(f"Comparando: '{v1_str}' com '{v2_str}'")
        
        # Converte para lista de inteiros
        v1 = [int(x) for x in v1_str.split('.')]
        v2 = [int(x) for x in v2_str.split('.')]
        
        print(f"V1 como lista: {v1}")
        print(f"V2 como lista: {v2}")
        
        # Preenche com zeros para igualar tamanhos
        max_len = max(len(v1), len(v2))
        v1.extend([0] * (max_len - len(v1)))
        v2.extend([0] * (max_len - len(v2)))
        
        print(f"V1 normalizada: {v1}")
        print(f"V2 normalizada: {v2}")
        
        # Compara cada posição
        for i in range(max_len):
            if v1[i] > v2[i]:
                print(f"Resultado: V1 > V2 (posição {i}: {v1[i]} > {v2[i]})")
                return 1
            elif v1[i] < v2[i]:
                print(f"Resultado: V1 < V2 (posição {i}: {v1[i]} < {v2[i]})")
                return -1
        
        print("Resultado: Versões iguais")
        return 0
        
    except Exception as e:
        print(f"Erro ao comparar versões: {e}")
        import traceback
        traceback.print_exc()
        return -1

def verificar_nova_versao():
    """
    Verifica se existe nova versão publicada no GitHub Releases.
    Retorna (nova_versao, url_download) se houver.
    """
    try:
        print(f"\n{'='*60}")
        print(f"Verificando atualizações...")
        print(f"Versão atual do sistema: '{VERSAO_ATUAL}'")
        print(f"{'='*60}\n")
        
        response = requests.get(REPO_API, timeout=15)
        response.raise_for_status()
        data = response.json()

        nova_versao = data["tag_name"].strip()
        print(f"Versão mais recente no GitHub: '{nova_versao}'")
        
        # Comparar versões
        resultado_comparacao = comparar_versoes(VERSAO_ATUAL, nova_versao)
        print(f"\nResultado da comparação: {resultado_comparacao}")
        
        # Se nova_versao <= VERSAO_ATUAL, não há atualização
        if resultado_comparacao >= 0:
            print("DECISÃO: Sistema já está na versão mais recente.")
            return None, None
        
        print("DECISÃO: Nova versão disponível!")

        # Buscar asset .exe
        print("\nBuscando arquivo .exe na release...")
        for asset in data.get("assets", []):
            asset_name = asset["name"].lower()
            print(f"  - Verificando asset: {asset['name']}")
            if asset_name.endswith(".exe") and "mbsistema" in asset_name:
                print(f"  ✓ Asset encontrado: {asset['name']}")
                print(f"  URL: {asset['browser_download_url']}")
                return nova_versao, asset["browser_download_url"]

        print("  ✗ Nenhum arquivo .exe compatível encontrado na release")
        return None, None

    except requests.exceptions.RequestException as e:
        print(f"Erro de conexão ao verificar nova versão: {e}")
        return None, None
    except Exception as e:
        print(f"Erro inesperado ao verificar nova versão: {e}")
        import traceback
        traceback.print_exc()
        return None, None

def baixar_nova_versao(url_download, destino, progress_callback=None):
    """
    Faz o download do executável mais recente.
    """
    try:
        print(f"\nIniciando download...")
        print(f"URL: {url_download}")
        print(f"Destino: {destino}")
        
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        response = requests.get(url_download, stream=True, timeout=60)
        response.raise_for_status()

        total_length = response.headers.get('content-length')
        with open(destino, 'wb') as f:
            if total_length is None:
                f.write(response.content)
                print("Download concluído (tamanho desconhecido)")
            else:
                dl = 0
                total_length = int(total_length)
                print(f"Tamanho total: {total_length / (1024*1024):.2f} MB")
                
                for data in response.iter_content(chunk_size=8192):
                    dl += len(data)
                    f.write(data)
                    
                    # Callback de progresso se fornecido
                    if progress_callback and total_length > 0:
                        progresso = int(100 * dl / total_length)
                        progress_callback(progresso)
                        
        print(f"Download concluído com sucesso: {destino}")
        return True
        
    except Exception as e:
        print(f"Erro ao baixar atualização: {e}")
        import traceback
        traceback.print_exc()
        
        # Limpa arquivo parcialmente baixado
        try:
            if os.path.exists(destino):
                os.remove(destino)
                print("Arquivo parcial removido")
        except:
            pass
        return False

def criar_script_atualizacao(current_exe, new_exe_path):
    """
    Cria o script de atualização com tratamento robusto de erros.
    """
    try:
        app_dir = os.path.dirname(current_exe)
        updater_script_path = os.path.join(app_dir, 'updater.bat')
        
        # Nomes dos arquivos
        current_exe_name = os.path.basename(current_exe)
        new_exe_name = os.path.basename(new_exe_path)
        
        print(f"\nCriando script de atualização...")
        print(f"Executável atual: {current_exe_name}")
        print(f"Novo executável: {new_exe_name}")
        print(f"Script: {updater_script_path}")
        
        script_content = f"""@echo off
chcp 65001 >nul
echo Iniciando processo de atualização...

:: Aguardar aplicação fechar completamente
echo Aguardando aplicação fechar...
timeout /t 3 /nobreak >nul

:: Tentar renomear o executável atual
if exist "{current_exe_name}" (
    echo Renomeando executável atual...
    ren "{current_exe_name}" "{current_exe_name}.old"
)

:: Copiar nova versão
if exist "atualizacao\\{new_exe_name}" (
    echo Instalando nova versão...
    copy /Y "atualizacao\\{new_exe_name}" "{current_exe_name}"
)

:: Verificar se a cópia foi bem-sucedida
if exist "{current_exe_name}" (
    echo Iniciando nova versão...
    start "" "{current_exe_name}"
    
    :: Limpeza após sucesso
    timeout /t 2 /nobreak >nul
    if exist "{current_exe_name}.old" (
        del "{current_exe_name}.old"
    )
    if exist "atualizacao\\{new_exe_name}" (
        del "atualizacao\\{new_exe_name}"
    )
    echo Atualização concluída com sucesso!
) else (
    echo ERRO: Falha na atualização!
    if exist "{current_exe_name}.old" (
        echo Restaurando versão anterior...
        ren "{current_exe_name}.old" "{current_exe_name}"
    )
    pause
)

:: Auto-deleção do script
timeout /t 1 /nobreak >nul
del "%~f0"
"""
        
        with open(updater_script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        print(f"Script criado com sucesso!")
        return updater_script_path
        
    except Exception as e:
        print(f"Erro ao criar script de atualização: {e}")
        import traceback
        traceback.print_exc()
        return None

def executar_atualizacao(progress_callback=None, status_callback=None):
    """
    Função principal: verifica, baixa e aplica se necessário.
    Retorna mensagem de status.
    """
    try:
        if status_callback:
            status_callback("Verificando atualizações...")
            
        nova_versao, url = verificar_nova_versao()
        if not nova_versao:
            return "Sistema já está na versão mais recente."

        if status_callback:
            status_callback(f"Nova versão {nova_versao} encontrada. Baixando...")
            
        # Definir destino do download
        app_dir = os.path.dirname(sys.executable)
        destino = os.path.join(app_dir, "atualizacao", "mbsistema.exe")
        
        # Fazer download
        sucesso = baixar_nova_versao(url, destino, progress_callback)
        
        if sucesso:
            if status_callback:
                status_callback("Download concluído. Preparando instalação...")
                
            # Criar e executar script de atualização
            script_path = criar_script_atualizacao(sys.executable, destino)
            if script_path:
                # Executar em processo separado
                subprocess.Popen([script_path], shell=True, 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                
                # Dar tempo para o script iniciar antes de fechar a aplicação
                time.sleep(2)
                return f"Atualização para versão {nova_versao} iniciada. O sistema será reiniciado."
            else:
                return "Erro ao preparar atualização."
        else:
            return "Falha ao baixar a atualização. Verifique sua conexão."
            
    except Exception as e:
        error_msg = f"Erro durante a atualização: {str(e)}"
        print(error_msg)
        import traceback
        traceback.print_exc()
        return error_msg

# Função auxiliar para uso direto (sem callbacks)
def verificar_e_baixar_atualizacao():
    """
    Versão simplificada para verificação e download de atualização.
    """
    nova_versao, url = verificar_nova_versao()
    if not nova_versao:
        return False, "Sistema já está na versão mais recente."
    
    app_dir = os.path.dirname(sys.executable)
    destino = os.path.join(app_dir, "atualizacao", "mbsistema.exe")
    
    sucesso = baixar_nova_versao(url, destino)
    if sucesso:
        return True, f"Versão {nova_versao} baixada com sucesso. Reinicie o sistema para instalar."
    else:
        return False, "Falha ao baixar a atualização."