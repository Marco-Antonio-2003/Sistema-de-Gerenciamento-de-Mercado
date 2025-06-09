"""
Módulo singleton para gerenciar o processo do Syncthing
"""

import os
import sys
import subprocess
import time
import atexit

class SyncthingManager:
    _instance = None
    _process = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SyncthingManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialized = True
            # Registrar função para encerrar o Syncthing quando a aplicação for fechada
            atexit.register(self.encerrar_syncthing)
    
    def iniciar_syncthing(self):
        """Inicia o Syncthing se ele não estiver em execução"""
        if self.verificar_syncthing_rodando():
            print("Syncthing já está em execução.")
            return True
            
        # Determinar possíveis caminhos para o Syncthing
        possiveis_caminhos = self._obter_possiveis_caminhos()
        
        # Tentar cada caminho possível
        syncthing_path = None
        for caminho in possiveis_caminhos:
            print(f"Verificando Syncthing em: {caminho}")
            if os.path.exists(caminho):
                syncthing_path = caminho
                print(f"Syncthing encontrado em: {syncthing_path}")
                break
        
        if not syncthing_path:
            print("ERRO: Syncthing não encontrado em nenhum local esperado!")
            return False
        
        # Iniciar o Syncthing com a flag -no-browser
        try:
            print(f"Iniciando Syncthing de: {syncthing_path}")
            if sys.platform == 'win32':
                # No Windows, usar startupinfo para esconder a janela de console
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                # Use o caminho absoluto completo
                self._process = subprocess.Popen(
                    [os.path.abspath(syncthing_path), "-no-browser"], 
                    startupinfo=startupinfo
                )
            else:
                # Em outros sistemas, iniciar em segundo plano
                self._process = subprocess.Popen(
                    [os.path.abspath(syncthing_path), "-no-browser"], 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL
                )
            
            # Aguardar um tempo para o Syncthing iniciar
            time.sleep(2)
            print("Syncthing iniciado com sucesso!")
            return True
            
        except Exception as e:
            print(f"Erro ao iniciar o processo do Syncthing: {e}")
            return False
    
    def verificar_syncthing_rodando(self):
        """Verifica se o Syncthing já está em execução"""
        try:
            # Se temos uma referência ao processo e ele ainda está rodando
            if self._process and self._process.poll() is None:
                return True
                
            # Verificar via sistema operacional
            if sys.platform == 'win32':
                output = subprocess.check_output("tasklist | findstr syncthing", shell=True)
                return b'syncthing' in output
            else:
                output = subprocess.check_output("ps -ef | grep syncthing | grep -v grep", shell=True)
                return len(output) > 0
        except subprocess.CalledProcessError:
            return False
        except Exception as e:
            print(f"Erro ao verificar status do Syncthing: {e}")
            return False
    
    def encerrar_syncthing(self):
        """Encerra o processo do Syncthing ao fechar a aplicação"""
        if self._process and self._process.poll() is None:
            try:
                self._process.terminate()
                # Dar tempo para encerrar graciosamente
                time.sleep(1)
                # Se ainda estiver rodando, forçar encerramento
                if self._process.poll() is None:
                    self._process.kill()
                print("Syncthing encerrado com sucesso!")
            except Exception as e:
                print(f"Erro ao encerrar Syncthing: {e}")
    
    def _obter_possiveis_caminhos(self):
        """Retorna possíveis caminhos para o executável do Syncthing"""
        possiveis_caminhos = []
        
        # Se estamos executando como um executável compilado
        if getattr(sys, 'frozen', False):
            # 1. Diretório do executável principal
            base_path = os.path.dirname(sys.executable)
            possiveis_caminhos.append(os.path.join(base_path, "syncthing.exe"))
            
            # 2. Diretório raiz do app (pode ser diferente se houver subdiretórios)
            possiveis_caminhos.append(os.path.join(os.path.dirname(base_path), "syncthing.exe"))
            
            # 3. Diretório atual
            possiveis_caminhos.append("syncthing.exe")
        else:
            # Em modo de desenvolvimento
            from base.banco import get_base_path
            base_path = get_base_path()
            possiveis_caminhos.append(os.path.join(base_path, "syncthing.exe"))
            possiveis_caminhos.append("syncthing.exe")
        
        return possiveis_caminhos

# Criar instância global
syncthing_manager = SyncthingManager()