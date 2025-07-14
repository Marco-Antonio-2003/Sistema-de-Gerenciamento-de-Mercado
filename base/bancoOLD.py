"""
Módulo para gerenciar conexões com o banco de dados Firebird
"""

#banco.py
from datetime import date
import os
import sys
import fdb  # Módulo para conexão com Firebird
from PyQt5.QtWidgets import QMessageBox
import hashlib
import base64
import time
import random
import string
import threading
import atexit
import functools

# Variáveis globais para controle de sincronização (adicione junto às outras variáveis globais)
SINCRONIZACAO_ATIVA = False
ULTIMA_SINCRONIZACAO = 0
INTERVALO_MIN_SYNC = 300  # 5 minutos entre sincronizações

# Função para encontrar o caminho do banco de dados
# Função adicionada para resolver problemas de caminho no executável
