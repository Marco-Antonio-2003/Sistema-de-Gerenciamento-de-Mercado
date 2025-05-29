import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
import random
import datetime

def gerar_cupom_pdf(id_venda, tipo_cupom, cpf, data_venda, itens, total, forma_pagamento, 
                    dir_saida="cupons", nome_empresa="MB SISTEMA", 
                    cnpj="000000000"):
    """
    Gera um PDF de cupom fiscal ou não fiscal
    
    Args:
        id_venda: ID da venda
        tipo_cupom: Tipo de cupom (FISCAL, NAO_FISCAL, CONTA_CREDITO)
        cpf: CPF do cliente (pode ser vazio)
        data_venda: Data da venda no formato datetime
        itens: Lista de dicionários com os itens da venda (dicionário deve ter: produto, quantidade, valor_unitario)
        total: Valor total da venda
        forma_pagamento: Forma de pagamento utilizada
        dir_saida: Diretório onde o PDF será salvo
        nome_empresa: Nome da empresa que aparecerá no cupom
        cnpj: CNPJ da empresa
        
    Returns:
        str: Caminho para o arquivo PDF gerado
    """
    # Criar diretório de saída se não existir
    if not os.path.exists(dir_saida):
        os.makedirs(dir_saida)
    
    # Gerar nome do arquivo
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    nome_arquivo = f"cupom_{tipo_cupom}_{id_venda}_{timestamp}.pdf"
    caminho_arquivo = os.path.join(dir_saida, nome_arquivo)
    
    # Definir tamanho do papel (uma tira de papel termico típica)
    largura = 80 * mm
    altura = 180 * mm
    
    # Criar o canvas
    c = canvas.Canvas(caminho_arquivo, pagesize=(largura, altura))
    c.setTitle(f"Cupom {tipo_cupom} - Venda #{id_venda}")
    
    # Definir fonte e tamanho
    c.setFont("Helvetica-Bold", 12)
    
    # Configurar margens
    margem_x = 5 * mm
    y_atual = altura - margem_x  # Começar do topo
    
    # ---------- CABEÇALHO ----------
    # Logo ou Nome da empresa
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(largura/2, y_atual, nome_empresa)
    y_atual -= 5 * mm
    
    # CNPJ
    c.setFont("Helvetica", 8)
    c.drawCentredString(largura/2, y_atual, f"CNPJ: {cnpj}")
    y_atual -= 4 * mm
    
    # Endereço
    c.setFont("Helvetica", 8)
    c.drawCentredString(largura/2, y_atual, "VILA SANTANA")
    y_atual -= 3 * mm
    c.drawCentredString(largura/2, y_atual, "EMILIO FARRARI, 110")
    y_atual -= 3 * mm
    c.drawCentredString(largura/2, y_atual, "ITAPEVA - SP")
    y_atual -= 5 * mm
    
    # Tipo de documento
    c.setFont("Helvetica-Bold", 9)
    if tipo_cupom == "FISCAL":
        c.drawCentredString(largura/2, y_atual, "Documento Auxiliar da Nota Fiscal de Consumidor Eletrônica")
    elif tipo_cupom == "NAO_FISCAL":
        c.drawCentredString(largura/2, y_atual, "CUPOM NÃO FISCAL")
        c.setFont("Helvetica", 7)
        y_atual -= 3 * mm
        c.drawCentredString(largura/2, y_atual, "Não permite aproveitamento de crédito de ICMS")
    elif tipo_cupom == "CONTA_CREDITO":
        c.drawCentredString(largura/2, y_atual, "COMPROVANTE DE CONTA CRÉDITO")
    
    y_atual -= 10 * mm
    
    # Linha separadora
    c.line(margem_x, y_atual, largura - margem_x, y_atual)
    y_atual -= 5 * mm
    
    # Informações da Venda
    c.setFont("Helvetica-Bold", 9)
    c.drawString(margem_x, y_atual, f"Venda #{id_venda}")
    y_atual -= 4 * mm
    
    c.setFont("Helvetica", 8)
    c.drawString(margem_x, y_atual, f"Data: {data_venda.strftime('%d/%m/%Y %H:%M:%S')}")
    y_atual -= 4 * mm
    
    # Se tem CPF, exibir
    if cpf:
        c.drawString(margem_x, y_atual, f"CPF: {cpf}")
        y_atual -= 4 * mm
    else:
        c.drawString(margem_x, y_atual, "CONSUMIDOR NÃO IDENTIFICADO")
        y_atual -= 4 * mm
    
    # Forma de pagamento
    c.drawString(margem_x, y_atual, f"Pagamento: {forma_pagamento}")
    y_atual -= 6 * mm
    
    # Linha separadora
    c.line(margem_x, y_atual, largura - margem_x, y_atual)
    y_atual -= 5 * mm
    
    # ---------- ITENS ----------
    # Cabeçalho da tabela de itens
    c.setFont("Helvetica-Bold", 8)
    c.drawString(margem_x, y_atual, "Item")
    c.drawString(margem_x + 25 * mm, y_atual, "Qtd")
    c.drawString(margem_x + 35 * mm, y_atual, "Vlr Unit")
    c.drawString(margem_x + 55 * mm, y_atual, "Total")
    y_atual -= 3 * mm
    
    c.line(margem_x, y_atual, largura - margem_x, y_atual)
    y_atual -= 5 * mm
    
    # Lista de itens
    c.setFont("Helvetica", 8)
    
    for i, item in enumerate(itens, 1):
        nome_produto = item['produto']
        if len(nome_produto) > 30:  # Se o nome for muito longo
            nome_produto = nome_produto[:27] + "..."
        
        # Número do item e nome do produto
        c.drawString(margem_x, y_atual, f"{i:02d} {nome_produto}")
        y_atual -= 4 * mm
        
        # Quantidade, valor unitário e total
        quantidade = item['quantidade']
        valor_unitario = float(item['valor_unitario'])
        valor_total = quantidade * valor_unitario
        
        c.drawString(margem_x + 25 * mm, y_atual, f"{quantidade}")
        c.drawString(margem_x + 35 * mm, y_atual, f"R$ {valor_unitario:.2f}".replace('.', ','))
        c.drawString(margem_x + 55 * mm, y_atual, f"R$ {valor_total:.2f}".replace('.', ','))
        y_atual -= 6 * mm
        
        # Se estiver chegando ao fim da página, criar nova página
        if y_atual < 50 * mm:
            c.showPage()
            c.setFont("Helvetica", 8)
            y_atual = altura - 20 * mm
    
    # Linha separadora
    c.line(margem_x, y_atual, largura - margem_x, y_atual)
    y_atual -= 5 * mm
    
    # ---------- TOTAIS ----------
    c.setFont("Helvetica-Bold", 9)
    
    # Desconto e acréscimo (valores de exemplo, substitua pelos valores reais)
    c.drawString(margem_x, y_atual, "Subtotal:")
    c.drawRightString(largura - margem_x, y_atual, f"R$ {total:.2f}".replace('.', ','))
    y_atual -= 4 * mm
    
    c.drawString(margem_x, y_atual, "Desconto:")
    c.drawRightString(largura - margem_x, y_atual, "R$ 0,00")
    y_atual -= 4 * mm
    
    c.drawString(margem_x, y_atual, "Acréscimo:")
    c.drawRightString(largura - margem_x, y_atual, "R$ 0,00")
    y_atual -= 4 * mm
    
    # Linha separadora
    c.line(margem_x, y_atual, largura - margem_x, y_atual)
    y_atual -= 5 * mm
    
    # Total a pagar
    c.setFont("Helvetica-Bold", 10)
    c.drawString(margem_x, y_atual, "TOTAL:")
    c.drawRightString(largura - margem_x, y_atual, f"R$ {total:.2f}".replace('.', ','))
    y_atual -= 15 * mm
    
    # ---------- MENSAGEM DE VERIFICAÇÃO ----------
    if tipo_cupom == "FISCAL":
        # Dados de autenticação (valores de exemplo)
        c.setFont("Helvetica", 7)
        chave_acesso = "".join([str(random.randint(0, 9)) for _ in range(44)])
        chave_formatada = " ".join([chave_acesso[i:i+4] for i in range(0, len(chave_acesso), 4)])
        
        c.drawCentredString(largura/2, y_atual, f"Consulte pela Chave de Acesso em:")
        y_atual -= 3 * mm
        c.drawCentredString(largura/2, y_atual, "www.fazenda.df.gov.br/nfce/consulta")
        y_atual -= 3 * mm
        
        c.drawCentredString(largura/2, y_atual, chave_formatada)
        y_atual -= 5 * mm
        
        if not cpf:
            c.drawCentredString(largura/2, y_atual, "CONSUMIDOR NÃO IDENTIFICADO")
            y_atual -= 3 * mm
        
        c.drawCentredString(largura/2, y_atual, f"NFCe n. 000000006 Série 002 {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        y_atual -= 3 * mm
        
        protocolo = f"353 {random.randint(100000000, 999999999)} {random.randint(10, 99)}"
        data_autorizacao = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        c.drawCentredString(largura/2, y_atual, f"Protocolo de Autorização: {protocolo}")
        y_atual -= 3 * mm
        c.drawCentredString(largura/2, y_atual, f"Data de Autorização: {data_autorizacao}")
    else:
        # Para documento não fiscal
        c.setFont("Helvetica-Bold", 10)
        if tipo_cupom == "NAO_FISCAL":
            c.drawCentredString(largura/2, y_atual, "SEM VALOR FISCAL")
            y_atual -= 5 * mm
            c.setFont("Helvetica", 8)
            c.drawCentredString(largura/2, y_atual, "Documento emitido em ambiente de")
            y_atual -= 3 * mm
            c.drawCentredString(largura/2, y_atual, "homologação")
        else:
            c.drawCentredString(largura/2, y_atual, "COMPROVANTE DE CRÉDITO")
    
    y_atual -= 10 * mm
    
    # ---------- AGRADECIMENTO ----------
    c.setFont("Helvetica", 8)
    c.drawCentredString(largura/2, y_atual, "Agradecemos a preferência!")
    y_atual -= 4 * mm
    
    c.drawCentredString(largura/2, y_atual, f"{nome_empresa} - " + datetime.datetime.now().strftime("%d/%m/%Y"))
    
    # Finalizar o PDF
    c.showPage()
    c.save()
    
    return caminho_arquivo