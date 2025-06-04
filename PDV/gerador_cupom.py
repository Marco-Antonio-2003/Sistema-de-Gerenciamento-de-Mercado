import os
import sys
import datetime
import subprocess
import platform
import time

# Importar funções do banco de dados
from base.banco import execute_query

def verificar_e_instalar_escpos():
    """Verifica se python-escpos está instalado e tenta instalar se não estiver"""
    try:
        from escpos.printer import Usb, Serial, Network, Win32Raw
        return True
    except ImportError:
        print("Módulo python-escpos não encontrado. Tentando instalar...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-escpos"])
            print("python-escpos instalado com sucesso!")
            print("IMPORTANTE: Reinicie o programa para que as alterações tenham efeito.")
            return False
        except Exception as e:
            print(f"Erro ao instalar python-escpos: {e}")
            print("Instale manualmente com: pip install python-escpos")
            return False


def obter_impressora_pdv():
    """
    Busca a impressora configurada como 'PDV' no banco.
    Aceita qualquer categoria que contenha 'PDV' (case-insensitive).
    Se não encontrar, faz fallback para a impressora térmica da estação.
    Returns:
        str | None: Nome da impressora ou None se não houver.
    """
    try:
        print("=== DEBUG: Iniciando busca de impressora PDV ===")
        
        # Primeiro, listar todas as configurações para debug
        try:
            print("Listando todas as configurações de impressoras:")
            todas_configs = execute_query("SELECT ID, CATEGORIA, IMPRESSORA, ESTACAO FROM CONFIGURACAO_IMPRESSORAS")
            if todas_configs:
                for config in todas_configs:
                    print(f"  ID: {config[0]}, Categoria: '{config[1]}', Impressora: '{config[2]}', Estação: '{config[3]}'")
            else:
                print("  Nenhuma configuração encontrada na tabela")
        except Exception as e:
            print(f"Erro ao listar configurações: {e}")
        
        # Busca específica por "PDV" exato
        print("\n1. Buscando por categoria exata 'PDV'...")
        try:
            result = execute_query("SELECT IMPRESSORA FROM CONFIGURACAO_IMPRESSORAS WHERE CATEGORIA = 'PDV'")
            print(f"Resultado busca exata 'PDV': {result}")
            if result and len(result) > 0 and result[0][0]:
                nome = result[0][0].strip()
                print(f"✅ Impressora PDV encontrada (busca exata): {nome}")
                return nome
        except Exception as e:
            print(f"Erro na busca exata: {e}")
        
        # Busca por "Impressora para o PDV" (baseado na sua imagem)
        print("\n2. Buscando por categoria 'Impressora para o PDV'...")
        try:
            result = execute_query("SELECT IMPRESSORA FROM CONFIGURACAO_IMPRESSORAS WHERE CATEGORIA = 'Impressora para o PDV'")
            print(f"Resultado busca 'Impressora para o PDV': {result}")
            if result and len(result) > 0 and result[0][0]:
                nome = result[0][0].strip()
                print(f"✅ Impressora PDV encontrada (busca específica): {nome}")
                return nome
        except Exception as e:
            print(f"Erro na busca específica: {e}")
        
        # Busca com LIKE para qualquer categoria que contenha PDV
        print("\n3. Buscando com LIKE %PDV%...")
        try:
            result = execute_query("SELECT IMPRESSORA, CATEGORIA FROM CONFIGURACAO_IMPRESSORAS WHERE UPPER(CATEGORIA) LIKE '%PDV%'")
            print(f"Resultado busca LIKE '%PDV%': {result}")
            if result and len(result) > 0 and result[0][0]:
                nome = result[0][0].strip()
                categoria = result[0][1] if len(result[0]) > 1 else "N/A"
                print(f"✅ Impressora PDV encontrada (busca LIKE): {nome} - Categoria: {categoria}")
                return nome
        except Exception as e:
            print(f"Erro na busca LIKE: {e}")
        
        # Busca mais ampla por qualquer impressora
        print("\n4. Buscando qualquer impressora...")
        try:
            result = execute_query("SELECT IMPRESSORA, CATEGORIA FROM CONFIGURACAO_IMPRESSORAS ORDER BY ID DESC")
            print(f"Resultado busca geral: {result}")
            if result and len(result) > 0:
                for row in result:
                    if row[0] and row[0].strip():
                        nome = row[0].strip()
                        categoria = row[1] if row[1] else "N/A"
                        print(f"✅ Impressora encontrada (busca geral): {nome} - Categoria: {categoria}")
                        return nome
        except Exception as e:
            print(f"Erro na busca geral: {e}")

        # Fallback para impressora térmica da estação
        print("\n5. Tentando fallback para CONFIG_ESTACAO...")
        try:
            result_fb = execute_query("SELECT IMPRESSORA_TERMICA FROM CONFIG_ESTACAO WHERE ATIVO = 1 ORDER BY ID DESC")
            print(f"Resultado fallback CONFIG_ESTACAO: {result_fb}")
            if result_fb and len(result_fb) > 0 and result_fb[0][0]:
                nome = result_fb[0][0].strip()
                print(f"✅ Impressora térmica encontrada (fallback): {nome}")
                return nome
        except Exception as e:
            print(f"Erro no fallback: {e}")

        print("❌ Nenhuma impressora configurada encontrada")
        return None

    except Exception as e:
        print(f"❌ Erro geral ao buscar impressora PDV: {e}")
        import traceback
        traceback.print_exc()
        return None

def conectar_impressora(nome_impressora):
    """
    Conecta com a impressora térmica usando diferentes métodos
    Args:
        nome_impressora (str): Nome da impressora
    Returns:
        object | None: Objeto da impressora conectada ou None
    """
    try:
        from escpos.printer import Win32Raw, Usb, Serial, Network
        
        print(f"Tentando conectar com a impressora: {nome_impressora}")
        
        # Tentativa Win32Raw no Windows (método mais comum para impressoras instaladas)
        if platform.system() == "Windows":
            try:
                print(f"Tentando Win32Raw com: {nome_impressora}")
                printer = Win32Raw(nome_impressora)
                
                # Teste básico de conexão
                printer._raw(b'\x1B\x40')  # ESC @ - Reset
                print(f"✅ Conectado via Win32Raw: {nome_impressora}")
                return printer
            except Exception as e:
                print(f"❌ Erro Win32Raw: {e}")
        
        # Se o nome contém informações sobre USB, tenta extrair vendor ID
        if "ELGIN" in nome_impressora.upper() or "i9" in nome_impressora.upper():
            # IDs comuns da Elgin
            vendor_ids = [0x20d1, 0x0483, 0x0519]
            for vid in vendor_ids:
                try:
                    printer = Usb(vid, 0x0001)
                    printer._raw(b'\x1B\x40')  # Teste de conexão
                    print(f"✅ Conectado via USB Elgin (vendor:{hex(vid)})")
                    return printer
                except:
                    try:
                        printer = Usb(vid, 0x0002)
                        printer._raw(b'\x1B\x40')  # Teste de conexão
                        print(f"✅ Conectado via USB Elgin (vendor:{hex(vid)}, product:0x0002)")
                        return printer
                    except:
                        continue
        
        # Tentativa USB genérica
        vendor_ids = [0x20d1, 0x0dd4, 0x0519, 0x0483]
        for vid in vendor_ids:
            try:
                printer = Usb(vid, 0x0001)
                printer._raw(b'\x1B\x40')  # Teste de conexão
                print(f"✅ Conectado via USB (vendor:{hex(vid)})")
                return printer
            except:
                try:
                    printer = Usb(vid, 0x0002)
                    printer._raw(b'\x1B\x40')  # Teste de conexão
                    print(f"✅ Conectado via USB (vendor:{hex(vid)}, product:0x0002)")
                    return printer
                except:
                    continue
        
        # Tentativa Serial
        portas_serial = ['COM1','COM2','COM3','COM4','COM5','COM6','/dev/ttyUSB0','/dev/ttyS0']
        for porta in portas_serial:
            try:
                if os.path.exists(porta) or porta.startswith('COM'):
                    printer = Serial(porta, baudrate=9600)
                    printer._raw(b'\x1B\x40')  # Teste de conexão
                    print(f"✅ Conectado via Serial: {porta}")
                    return printer
            except:
                continue
        
        # Tentativa Network
        ips_rede = ['192.168.1.100','192.168.0.100','10.0.0.100','127.0.0.1']
        for ip in ips_rede:
            try:
                printer = Network(ip, port=9100)
                printer._raw(b'\x1B\x40')  # Teste de conexão
                print(f"✅ Conectado via Network: {ip}")
                return printer
            except:
                continue
        
        print("❌ Não foi possível conectar com a impressora pelos métodos disponíveis")
        return None
        
    except ImportError:
        print("❌ Biblioteca python-escpos não está instalada")
        return None
    except Exception as e:
        print(f"❌ Erro geral ao conectar: {e}")
        import traceback
        traceback.print_exc()
        return None

def gerar_cupom_escpos_seguro(printer, id_venda, tipo_cupom, cpf, data_venda, itens, total, 
                             forma_pagamento, nome_empresa="MB SISTEMA", 
                             cnpj="00.000.000/0001-00"):
    """
    Versão mais segura da função de impressão com tratamento robusto de erros e com
    **todos** os textos centralizados via ESC a 1.
    """
    try:
        print("🖨️ [PASSO 1] Iniciando impressão do cupom...")
        # Reset e selecionar alinhamento central para todo o cupom
        printer._raw(b'\x1B\x40')  # ESC @ - Reset
        time.sleep(0.2)
        printer._raw(b'\x1B\x61\x01')  # ESC a 1 - Center

        # ---------- CABEÇALHO ----------
        print("📝 [PASSO 2] Imprimindo cabeçalho...")
        printer.text("\n")
        printer.text(f"{nome_empresa}\n")
        printer.text(f"CNPJ: {cnpj}\n")
        printer.text("VILA SANTANA\n")
        printer.text("EMILIO FERRARI, 110\n")
        printer.text("ITAPEVA - SP\n\n")
        printer.text(f"CUPOM {tipo_cupom.replace('_', ' ')}\n")
        if tipo_cupom == "NAO_FISCAL":
            printer.text("Nao permite aproveitamento\n")
            printer.text("de credito de ICMS\n")
        printer.text("\n" + "=" * 32 + "\n")
        print("✅ [PASSO 2] Cabeçalho OK")

        # ---------- INFORMAÇÕES DA VENDA ----------
        print("📝 [PASSO 3] Imprimindo informações da venda...")
        printer.text(f"Venda #{id_venda}\n")
        printer.text(f"Data: {data_venda.strftime('%d/%m/%Y %H:%M:%S')}\n")
        if cpf and cpf.strip():
            printer.text(f"CPF: {cpf}\n")
        else:
            printer.text("CONSUMIDOR NAO IDENTIFICADO\n")
        printer.text(f"Pagamento: {forma_pagamento}\n")
        printer.text("\n" + "-" * 32 + "\n")
        print("✅ [PASSO 3] Informações da venda OK")

        # ---------- ITENS ----------
        print("📝 [PASSO 4] Imprimindo itens...")
        printer.text("ITEM  QTD  VALOR    TOTAL\n")
        printer.text("-" * 32 + "\n")
        for i, item in enumerate(itens, 1):
            nome_produto = str(item['produto'])[:20]
            quantidade = float(item['quantidade'])
            valor_unitario = float(item['valor_unitario'])
            valor_total_item = quantidade * valor_unitario
            printer.text(f"{i:02d} - {nome_produto}\n")
            linha_valores = f"{quantidade:3.0f} x {valor_unitario:6.2f} = {valor_total_item:6.2f}\n"
            printer.text(linha_valores.replace('.', ','))
            printer.text("-" * 32 + "\n")
            print(f"✅ [PASSO 4.{i}] Item {nome_produto} OK")
        print("✅ [PASSO 4] Todos os itens OK")

        # ---------- TOTAIS ----------
        print("📝 [PASSO 5] Imprimindo totais...")
        total_float = float(total)
        printer.text(f"Subtotal: R$ {total_float:6.2f}\n".replace('.', ','))
        printer.text(f"Desconto: R$   0,00\n")
        printer.text(f"Acrescimo: R$   0,00\n")
        printer.text("=" * 32 + "\n")
        printer.text(f"TOTAL: R$ {total_float:6.2f}\n".replace('.', ','))
        printer.text("=" * 32 + "\n")
        print("✅ [PASSO 5] Totais OK")

        # ---------- RODAPÉ ----------
        print("📝 [PASSO 6] Imprimindo rodapé...")
        if tipo_cupom == "NAO_FISCAL":
            printer.text("SEM VALOR FISCAL\n")
            printer.text("Documento emitido em ambiente\n")
            printer.text("de homologacao\n\n")
        printer.text("Agradecemos a preferencia!\n")
        printer.text(f"{nome_empresa}\n")
        printer.text(f"{data_venda.strftime('%d/%m/%Y')}\n\n")
        print("✅ [PASSO 6] Rodapé OK")

        # ---------- FINALIZAÇÃO ----------
        print("✂️ [PASSO 7] Finalizando impressão...")
        try:
            printer.cut()
            print("✅ [PASSO 7.1] Papel cortado")
        except:
            printer.text("\n" * 4)
            print("⚠️ [PASSO 7.1] Corte não suportado, alimentando papel")
        print("✅ [PASSO 7] Finalização OK")

        print("🎉 Cupom impresso com sucesso!")
        return True

    except Exception as e:
        print(f"❌ ERRO CRÍTICO na impressão: {e}")
        import traceback; traceback.print_exc()
        return False



def gerar_cupom_escpos(printer, id_venda, tipo_cupom, cpf, data_venda, itens, total, 
                      forma_pagamento, nome_empresa="MB SISTEMA", 
                      cnpj="00.000.000/0001-00"):
    """
    Função principal que chama a versão segura
    """
    return gerar_cupom_escpos_seguro(printer, id_venda, tipo_cupom, cpf, data_venda, itens, total, 
                                   forma_pagamento, nome_empresa, cnpj)

def gerar_e_imprimir_cupom(id_venda, tipo_cupom, cpf, data_venda, itens, total, forma_pagamento, 
                          nome_empresa="MB SISTEMA", cnpj="00.000.000/0001-00", 
                          imprimir_automaticamente=True):
    """
    Gera e imprime cupom diretamente na impressora térmica usando ESC/POS
    
    Args:
        id_venda: ID da venda
        tipo_cupom: Tipo de cupom (FISCAL, NAO_FISCAL, CONTA_CREDITO)
        cpf: CPF do cliente (pode ser vazio)
        data_venda: Data da venda no formato datetime
        itens: Lista de dicionários com os itens da venda
        total: Valor total da venda
        forma_pagamento: Forma de pagamento utilizada
        nome_empresa: Nome da empresa
        cnpj: CNPJ da empresa
        imprimir_automaticamente: Se True, imprime automaticamente
        
    Returns:
        dict: Dicionário com informações sobre o resultado
    """
    resultado = {
        'sucesso': False,
        'impressao_sucesso': False,
        'mensagem': '',
        'impressora_utilizada': None,
        'erro_detalhado': None
    }
    
    try:
        print("\n" + "="*60)
        print("🖨️ INICIANDO PROCESSO DE IMPRESSÃO DE CUPOM")
        print("="*60)
        
        if not imprimir_automaticamente:
            resultado['sucesso'] = True
            resultado['mensagem'] = 'Cupom não foi configurado para impressão automática'
            return resultado
        
        # Validar dados de entrada
        print("🔍 Validando dados de entrada...")
        if not id_venda:
            resultado['mensagem'] = 'ID da venda não informado'
            return resultado
            
        if not itens or len(itens) == 0:
            resultado['mensagem'] = 'Nenhum item informado para impressão'
            return resultado
            
        if not isinstance(data_venda, datetime.datetime):
            resultado['mensagem'] = 'Data da venda deve ser um objeto datetime'
            return resultado
        
        print(f"✅ Dados validados - Venda #{id_venda}, {len(itens)} itens, Total: R$ {total}")
        
        # Buscar a impressora PDV configurada
        print("\n🔍 Buscando impressora configurada...")
        impressora_pdv = obter_impressora_pdv()
        
        if not impressora_pdv:
            resultado['mensagem'] = 'Nenhuma impressora PDV configurada no banco de dados'
            resultado['erro_detalhado'] = 'Verifique a tabela CONFIGURACAO_IMPRESSORAS'
            print(f"❌ {resultado['mensagem']}")
            return resultado
        
        print(f"✅ Impressora encontrada: {impressora_pdv}")
        
        # Conectar com a impressora
        print("\n🔌 Conectando com a impressora...")
        printer = conectar_impressora(impressora_pdv)
        
        if not printer:
            resultado['mensagem'] = f'Não foi possível conectar com a impressora: {impressora_pdv}'
            resultado['erro_detalhado'] = 'Verifique se a impressora está ligada e os drivers instalados'
            print(f"❌ {resultado['mensagem']}")
            return resultado
        
        print("✅ Impressora conectada com sucesso!")
        
        # Gerar e imprimir o cupom
        print("\n📄 Gerando cupom...")
        impressao_ok = gerar_cupom_escpos(
            printer, id_venda, tipo_cupom, cpf, data_venda, itens, 
            total, forma_pagamento, nome_empresa, cnpj
        )
        
        if impressao_ok:
            resultado['sucesso'] = True
            resultado['impressao_sucesso'] = True
            resultado['impressora_utilizada'] = impressora_pdv
            resultado['mensagem'] = f'Cupom impresso com sucesso em {impressora_pdv}'
            print(f"\n🎉 {resultado['mensagem']}")
        else:
            resultado['mensagem'] = 'Falha ao gerar/imprimir o conteúdo do cupom'
            resultado['erro_detalhado'] = 'Erro durante a geração do cupom ESC/POS'
            print(f"❌ {resultado['mensagem']}")
        
        # Fechar conexão
        print("\n🔌 Fechando conexão com a impressora...")
        try:
            printer.close()
            print("✅ Conexão fechada")
        except Exception as e:
            print(f"⚠️ Aviso ao fechar conexão: {e}")
        
        return resultado
        
    except Exception as e:
        resultado['mensagem'] = f'Erro crítico ao gerar/imprimir cupom: {str(e)}'
        resultado['erro_detalhado'] = str(e)
        print(f"❌ ERRO CRÍTICO em gerar_e_imprimir_cupom: {e}")
        import traceback
        traceback.print_exc()
        return resultado

def teste_impressora_basico():
    """Teste mais básico possível para isolar problemas"""
    print("\n" + "="*50)
    print("🔬 TESTE ULTRA BÁSICO DE IMPRESSORA")
    print("="*50)
    
    try:
        # Buscar impressora
        print("1️⃣ Buscando impressora...")
        impressora_pdv = obter_impressora_pdv()
        if not impressora_pdv:
            print("❌ Nenhuma impressora encontrada")
            return False
        print(f"✅ Impressora: {impressora_pdv}")
        
        # Conectar
        print("2️⃣ Conectando...")
        printer = conectar_impressora(impressora_pdv)
        if not printer:
            print("❌ Falha na conexão")
            return False
        print("✅ Conectado")
        
        # Teste super simples
        print("3️⃣ Teste de impressão mínima...")
        try:
            printer.text("\n")
            printer.text("\n")
            printer.text("\n\n")
            print("✅ Impressão básica OK")
        except Exception as e:
            print(f"❌ Erro na impressão básica: {e}")
            return False
        
        # Fechar
        print("4️⃣ Fechando conexão...")
        try:
            printer.close()
            print("✅ Conexão fechada")
        except:
            pass
        
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste básico: {e}")
        import traceback
        traceback.print_exc()
        return False

def teste_impressora():
    """Função para testar a conectividade com a impressora"""
    print("\n" + "="*50)
    print("🧪 TESTE DE IMPRESSORA TÉRMICA")
    print("="*50)
    
    # Verificar se a biblioteca está instalada
    print("1️⃣ Verificando biblioteca python-escpos...")
    if not verificar_e_instalar_escpos():
        print("❌ Biblioteca não instalada. Execute novamente após reiniciar.")
        return False
    print("✅ Biblioteca instalada")
    
    # Teste ultra básico primeiro
    print("\n🔬 Executando teste ultra básico...")
    if not teste_impressora_basico():
        print("❌ Falha no teste básico")
        return False
    
    # Buscar impressora configurada
    print("\n2️⃣ Buscando impressora configurada...")
    impressora_pdv = obter_impressora_pdv()
    
    if not impressora_pdv:
        print("❌ Nenhuma impressora configurada no banco de dados")
        return False
    
    print(f"✅ Impressora configurada: {impressora_pdv}")
    
    # Tentar conectar
    print("\n3️⃣ Testando conexão...")
    printer = conectar_impressora(impressora_pdv)
    
    if not printer:
        print("❌ Não foi possível conectar com a impressora")
        return False
    
    print("✅ Impressora conectada com sucesso!")
    
    # Fazer teste básico de impressão
    print("\n4️⃣ Executando teste de impressão...")
    try:
        printer.set(align='center', text_type='B')
        printer.text("=== TESTE DE IMPRESSAO ===\n")
        printer.set(text_type='normal')
        printer.text(f"Data: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        printer.text("Impressora funcionando!\n")
        printer.text("Conexao: OK\n")
        printer.text("Comunicacao: OK\n")
        printer.text("=" * 30 + "\n")
        
        try:
            printer.cut()
        except:
            printer.text("\n\n")
        
        print("✅ Teste de impressão realizado com sucesso!")
        
        # Fechar conexão
        printer.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de impressão: {e}")
        import traceback
        traceback.print_exc()
        return False

# Função adicional para debug detalhado
def debug_sistema_impressao():
    """Função para debug completo do sistema de impressão"""
    print("\n" + "="*60)
    print("🔧 DEBUG COMPLETO DO SISTEMA DE IMPRESSÃO")
    print("="*60)
    
    print(f"🖥️ Sistema Operacional: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Verificar biblioteca
    print("\n📚 Verificando bibliotecas...")
    try:
        import escpos
        print(f"✅ python-escpos versão: {escpos.__version__}")
    except ImportError:
        print("❌ python-escpos não instalada")
    except AttributeError:
        print("✅ python-escpos instalada (versão não detectada)")
    
    # Verificar banco de dados
    print("\n🗄️ Verificando configurações no banco...")
    try:
        configs = execute_query("SELECT * FROM CONFIGURACAO_IMPRESSORAS")
        if configs:
            print(f"✅ Encontradas {len(configs)} configurações de impressora")
            for config in configs:
                print(f"   - {config}")
        else:
            print("❌ Nenhuma configuração encontrada")
    except Exception as e:
        print(f"❌ Erro ao acessar banco: {e}")
    
    # Tentar conexões
    print("\n🔌 Testando métodos de conexão...")
    impressora = obter_impressora_pdv()
    if impressora:
        conectar_impressora(impressora)

# Exemplo de uso
if __name__ == "__main__":
    print("🖨️ SISTEMA DE IMPRESSÃO TÉRMICA ESC/POS")
    print("="*50)
    
    # Debug completo se solicitado
    if len(sys.argv) > 1 and sys.argv[1] == "--debug":
        debug_sistema_impressao()
        sys.exit(0)
    
    # Verificar se python-escpos está instalado
    print("1️⃣ Verificando dependências...")
    if not verificar_e_instalar_escpos():
        print("❌ Por favor, reinicie o programa após a instalação da biblioteca")
        sys.exit(1)
    
    # Fazer teste da impressora
    print("\n2️⃣ Testando impressora...")
    if not teste_impressora():
        print("\n❌ FALHA NO TESTE DA IMPRESSORA")
        print("📋 Verifique:")
        print("   • Impressora está ligada e conectada")
        print("   • Drivers estão instalados corretamente")
        print("   • Configuração está correta no banco de dados")
        print("   • Papel está carregado")
        print("\n💡 Execute com --debug para mais informações:")
        print("   python seu_script.py --debug")
        sys.exit(1)
    
    print("\n3️⃣ Gerando cupom de exemplo...")
    
    # Dados de exemplo para teste
    itens_exemplo = [
        {'produto': 'Herbissimo', 'quantidade': 1, 'valor_unitario': 7.00},
        {'produto': 'Cafe Premium', 'quantidade': 2, 'valor_unitario': 15.50},
        {'produto': 'Acucar Cristal', 'quantidade': 1, 'valor_unitario': 4.20}
    ]
    
    total_exemplo = sum(item['quantidade'] * item['valor_unitario'] for item in itens_exemplo)
    
    # Chamar a função para gerar e imprimir automaticamente
    resultado = gerar_e_imprimir_cupom(
        id_venda=37,
        tipo_cupom="NAO_FISCAL",
        cpf="",  # Consumidor não identificado
        data_venda=datetime.datetime.now(),
        itens=itens_exemplo,
        total=total_exemplo,
        forma_pagamento="01 - Dinheiro",
        nome_empresa="MB SISTEMA",
        cnpj="00.000.000/0001-00",
        imprimir_automaticamente=True
    )
    
    print(f"\n" + "="*50)
    print("📊 RESULTADO DA OPERAÇÃO")
    print("="*50)
    print(f"✅ Sucesso Geral: {resultado['sucesso']}")
    print(f"🖨️ Impressão: {resultado['impressao_sucesso']}")
    print(f"📄 Impressora: {resultado['impressora_utilizada']}")
    print(f"💬 Mensagem: {resultado['mensagem']}")
    if resultado.get('erro_detalhado'):
        print(f"🔍 Erro Detalhado: {resultado['erro_detalhado']}")
    
    if resultado['impressao_sucesso']:
        print("\n🎉 CUPOM IMPRESSO COM SUCESSO!")
    else:
        print(f"\n❌ FALHA NA IMPRESSÃO")
        print(f"💬 {resultado['mensagem']}")
        if resultado.get('erro_detalhado'):
            print(f"🔍 {resultado['erro_detalhado']}")
        print("\n💡 Dicas para solução:")   
        print("   • Verifique se a impressora está ligada")
        print("   • Confirme se há papel na impressora")
        print("   • Teste a impressora no Windows")
        print("   • Execute com --debug para mais detalhes")