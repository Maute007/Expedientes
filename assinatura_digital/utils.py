"""
Utilitários para processamento de assinaturas em documentos
"""
import os
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image
import tempfile

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfutils
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import PyPDF2
    from PyPDF2 import PdfReader, PdfWriter
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False


def criar_backup_arquivo(arquivo_field):
    """
    Cria um backup do arquivo original antes de modificar
    Retorna o caminho relativo do backup (string) para armazenar no banco
    """
    if not arquivo_field:
        return None
    
    try:
        # Ler o arquivo original
        arquivo_field.open('rb')
        conteudo = arquivo_field.read()
        arquivo_field.close()
        
        # Criar nome do backup (limitar tamanho para evitar problemas)
        nome_original = os.path.basename(arquivo_field.name)
        
        # Limitar tamanho do nome do arquivo para evitar problemas
        # O caminho completo será: expedientes/anexos/backups/backup_{nome}
        # Precisamos garantir que o caminho completo não exceda 500 caracteres
        # Tamanho do prefixo: "expedientes/anexos/backups/backup_" = 37 caracteres
        # Então o nome do arquivo pode ter no máximo: 500 - 37 = 463 caracteres
        # Mas vamos ser mais conservadores e limitar a 200 caracteres
        if len(nome_original) > 200:
            nome_base, ext = os.path.splitext(nome_original)
            # Limitar nome base para deixar espaço para extensão e prefixo
            max_base_length = 200 - len(ext) - 10  # 10 caracteres de margem
            nome_original = nome_base[:max_base_length] + ext
        
        nome_backup = f"backup_{nome_original}"
        caminho_backup = f"expedientes/anexos/backups/{nome_backup}"
        
        # Verificar se o caminho completo não excede 500 caracteres
        if len(caminho_backup) > 500:
            # Se exceder, usar apenas o nome do arquivo
            caminho_backup = nome_backup
            if len(caminho_backup) > 500:
                # Se ainda exceder, truncar
                caminho_backup = caminho_backup[:500]
        
        # Salvar backup
        arquivo_backup_path = default_storage.save(caminho_backup, ContentFile(conteudo))
        
        # Retornar apenas o caminho relativo (string) ao invés do objeto FileField
        # Limitar o tamanho do caminho para evitar problemas com campos CharField
        # O campo no modelo tem max_length=500, então vamos garantir que não exceda
        if len(arquivo_backup_path) > 500:
            # Se o caminho for muito longo, usar apenas o nome do arquivo
            arquivo_backup_path = os.path.basename(arquivo_backup_path)
            if len(arquivo_backup_path) > 500:
                # Se ainda for muito longo, truncar
                arquivo_backup_path = arquivo_backup_path[:500]
        
        return arquivo_backup_path
    except Exception as e:
        print(f"Erro ao criar backup: {e}")
        return None


def inserir_assinatura_pdf(arquivo_pdf, assinatura_imagem, posicao_x, posicao_y, pagina=1):
    """
    Insere uma assinatura em um arquivo PDF
    
    Args:
        arquivo_pdf: FileField ou caminho do arquivo PDF
        assinatura_imagem: ContentFile, ImageField ou caminho da imagem da assinatura
        posicao_x: Posição X no documento
        posicao_y: Posição Y no documento
        pagina: Número da página (1-indexed)
    
    Returns:
        BytesIO com o PDF modificado
    """
    # Ler o arquivo PDF
    if hasattr(arquivo_pdf, 'path'):
        # É um FileField do Django
        with open(arquivo_pdf.path, 'rb') as f:
            pdf_content = f.read()
    elif hasattr(arquivo_pdf, 'read'):
        # É um arquivo aberto ou ContentFile
        pdf_content = arquivo_pdf.read()
        if hasattr(arquivo_pdf, 'seek'):
            arquivo_pdf.seek(0)
    else:
        # É um caminho string
        with open(arquivo_pdf, 'rb') as f:
            pdf_content = f.read()
    
    # Ler a imagem da assinatura
    if isinstance(assinatura_imagem, ContentFile):
        # É um ContentFile - ler diretamente
        assinatura_imagem.seek(0)
        signature_image = Image.open(BytesIO(assinatura_imagem.read()))
    elif hasattr(assinatura_imagem, 'path'):
        # É um ImageField do Django
        with open(assinatura_imagem.path, 'rb') as f:
            signature_image = Image.open(BytesIO(f.read()))
    elif hasattr(assinatura_imagem, 'read'):
        # É um arquivo aberto
        assinatura_imagem.seek(0)
        signature_image = Image.open(assinatura_imagem)
    else:
        # É um caminho string
        signature_image = Image.open(assinatura_imagem)
    
    # Converter imagem para PNG se necessário
    if signature_image.format != 'PNG':
        output = BytesIO()
        signature_image.save(output, format='PNG')
        signature_image = Image.open(output)
    
    # Redimensionar assinatura se muito grande (máximo 200x100 pixels)
    max_width, max_height = 200, 100
    if signature_image.width > max_width or signature_image.height > max_height:
        signature_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Salvar assinatura em buffer temporário
    signature_buffer = BytesIO()
    signature_image.save(signature_buffer, format='PNG')
    signature_buffer.seek(0)
    
    # Tentar usar PyPDF2 primeiro (mais simples)
    if PYPDF2_AVAILABLE:
        try:
            return _inserir_assinatura_pypdf2(pdf_content, signature_buffer, posicao_x, posicao_y, pagina)
        except Exception as e:
            print(f"Erro ao usar PyPDF2: {e}")
            # Tentar reportlab como fallback
    
    # Usar reportlab
    if REPORTLAB_AVAILABLE:
        try:
            return _inserir_assinatura_reportlab(pdf_content, signature_buffer, posicao_x, posicao_y, pagina)
        except Exception as e:
            print(f"Erro ao usar reportlab: {e}")
            raise Exception("Não foi possível inserir assinatura no PDF. Verifique se PyPDF2 ou reportlab estão instalados.")
    
    raise Exception("Nenhuma biblioteca de PDF disponível. Instale PyPDF2 ou reportlab.")


def _inserir_assinatura_pypdf2(pdf_content, signature_buffer, posicao_x, posicao_y, pagina):
    """
    Insere assinatura usando PyPDF2
    """
    # Ler PDF
    pdf_reader = PdfReader(BytesIO(pdf_content))
    pdf_writer = PdfWriter()
    
    # Copiar todas as páginas
    for i, page in enumerate(pdf_reader.pages):
        if i == (pagina - 1):  # Página é 1-indexed
            # Adicionar imagem na página
            # PyPDF2 não suporta diretamente, então vamos usar reportlab para isso
            # Por enquanto, vamos retornar o PDF sem modificação e usar reportlab
            pass
        pdf_writer.add_page(page)
    
    # Se PyPDF2 não suportar, usar reportlab
    return _inserir_assinatura_reportlab(pdf_content, signature_buffer, posicao_x, posicao_y, pagina)


def _inserir_assinatura_reportlab(pdf_content, signature_buffer, posicao_x, posicao_y, pagina):
    """
    Insere assinatura usando reportlab e PyPDF2 para mesclar
    """
    if not PYPDF2_AVAILABLE:
        raise Exception("PyPDF2 é necessário para processar PDFs. Instale: pip install PyPDF2")
    
    try:
        from reportlab.pdfgen import canvas
        from reportlab.lib.utils import ImageReader
        from PyPDF2 import PdfReader, PdfWriter
        
        # Ler PDF original
        pdf_reader = PdfReader(BytesIO(pdf_content))
        pdf_writer = PdfWriter()
        
        # Verificar se a página existe
        if pagina > len(pdf_reader.pages):
            raise Exception(f"Página {pagina} não existe no PDF. O PDF tem {len(pdf_reader.pages)} página(s).")
        
        # Obter tamanho da página específica onde a assinatura será inserida
        target_page = pdf_reader.pages[pagina - 1]  # Página é 1-indexed
        page_width = float(target_page.mediabox.width)
        page_height = float(target_page.mediabox.height)
        
        # IMPORTANTE: As coordenadas do frontend vêm em pixels do canvas renderizado
        # Mas já foram convertidas para coordenadas do PDF real no JavaScript
        # Se não foram convertidas, assumimos que são coordenadas relativas ao canvas
        # Por enquanto, vamos usar as coordenadas diretamente (assumindo que já foram convertidas)
        # Se necessário, podemos ajustar aqui
        
        # Garantir que as coordenadas estão dentro dos limites
        signature_width = 200  # pontos
        signature_height = 100  # pontos
        
        # Ajustar posição se necessário
        if posicao_x + signature_width > page_width:
            posicao_x = page_width - signature_width
        if posicao_x < 0:
            posicao_x = 0
        
        # Criar PDF temporário com a assinatura na página correta
        signature_pdf = BytesIO()
        # Usar o tamanho da página específica do PDF (converter para pontos do ReportLab)
        # ReportLab usa pontos (1/72 de polegada), então precisamos converter
        # Os mediabox já estão em pontos, então podemos usar diretamente
        c = canvas.Canvas(signature_pdf, pagesize=(page_width, page_height))
        
        # Adicionar imagem da assinatura
        signature_image = ImageReader(signature_buffer)
        
        # IMPORTANTE: Ajustar posição Y para o sistema de coordenadas do ReportLab
        # ReportLab usa origem no canto inferior esquerdo (Y=0 é no fundo)
        # As coordenadas do frontend vêm do canto superior esquerdo (Y=0 é no topo)
        # Precisamos inverter: y_reportlab = altura_pagina - y_frontend - altura_assinatura
        # Mas as coordenadas já vêm convertidas para pontos do PDF, então usamos diretamente
        
        # A posição Y do frontend é medida do topo, então precisamos inverter para o ReportLab
        # No ReportLab: Y=0 está no fundo, então: y_reportlab = page_height - y_frontend - signature_height
        y_reportlab = page_height - posicao_y - signature_height
        
        # Garantir que Y não seja negativo
        if y_reportlab < 0:
            y_reportlab = 0
        
        # Garantir que a assinatura não saia da página
        if posicao_x + signature_width > page_width:
            posicao_x = max(0, page_width - signature_width)
        if y_reportlab + signature_height > page_height:
            y_reportlab = max(0, page_height - signature_height)
        
        # Debug: imprimir coordenadas
        print(f"DEBUG: Posição recebida do frontend - X: {posicao_x}, Y: {posicao_y}")
        print(f"DEBUG: Tamanho página - Width: {page_width}, Height: {page_height}")
        print(f"DEBUG: Posição Y convertida para ReportLab: {y_reportlab}")
        print(f"DEBUG: Tamanho assinatura - Width: {signature_width}, Height: {signature_height}")
        
        # Desenhar a imagem da assinatura
        # Usar mask='auto' para suportar transparência PNG
        try:
            c.drawImage(signature_image, posicao_x, y_reportlab, width=signature_width, height=signature_height, preserveAspectRatio=True, mask='auto')
            print(f"DEBUG: Imagem desenhada com sucesso")
        except Exception as e:
            print(f"DEBUG: Erro ao desenhar imagem: {e}")
            raise
        c.save()
        signature_pdf.seek(0)
        
        # Verificar se o PDF da assinatura foi criado corretamente
        signature_pdf_size = len(signature_pdf.getvalue())
        if signature_pdf_size == 0:
            raise Exception("Erro ao criar PDF da assinatura: PDF está vazio.")
        
        # Ler PDF da assinatura
        signature_reader = PdfReader(signature_pdf)
        
        if len(signature_reader.pages) == 0:
            raise Exception("Erro ao criar PDF da assinatura: PDF está vazio.")
        
        # Mesclar páginas
        print(f"DEBUG: Iniciando mesclagem. Total de páginas PDF: {len(pdf_reader.pages)}, Página alvo: {pagina}")
        print(f"DEBUG: PDF da assinatura tem {len(signature_reader.pages)} página(s)")
        
        for i, page in enumerate(pdf_reader.pages):
            if i == (pagina - 1):  # Página é 1-indexed
                # Mesclar página da assinatura com a página original
                try:
                    signature_page = signature_reader.pages[0]
                    print(f"DEBUG: Mesclando assinatura na página {pagina} (índice {i})")
                    
                    # Verificar tamanhos das páginas
                    original_size = (float(page.mediabox.width), float(page.mediabox.height))
                    signature_size = (float(signature_page.mediabox.width), float(signature_page.mediabox.height))
                    print(f"DEBUG: Tamanho página original: {original_size}")
                    print(f"DEBUG: Tamanho página assinatura: {signature_size}")
                    
                    # Usar merge_page para mesclar as páginas
                    # merge_page coloca a página de assinatura sobre a original
                    page.merge_page(signature_page)
                    print(f"DEBUG: Mesclagem concluída com sucesso")
                except Exception as e:
                    # Se houver erro na mesclagem, re-raise para ver o erro
                    print(f"DEBUG: Erro na mesclagem: {e}")
                    import traceback
                    traceback.print_exc()
                    raise Exception(f"Erro ao mesclar assinatura na página {pagina}: {str(e)}")
            pdf_writer.add_page(page)
        
        # Salvar PDF final
        output = BytesIO()
        pdf_writer.write(output)
        output.seek(0)
        
        # Verificar se o output tem conteúdo
        output_size = len(output.getvalue())
        print(f"DEBUG: Tamanho do PDF final: {output_size} bytes")
        
        if output_size == 0:
            raise Exception("Erro ao gerar PDF: PDF final está vazio.")
        
        # Verificar se o PDF final tem o mesmo número de páginas
        output.seek(0)
        output_reader = PdfReader(output)
        output.seek(0)  # Voltar ao início novamente
        
        print(f"DEBUG: PDF final tem {len(output_reader.pages)} página(s), PDF original tinha {len(pdf_reader.pages)} página(s)")
        
        if len(output_reader.pages) != len(pdf_reader.pages):
            raise Exception(f"Erro: PDF final tem {len(output_reader.pages)} páginas, mas deveria ter {len(pdf_reader.pages)}")
        
        return output
        
    except Exception as e:
        raise Exception(f"Erro ao processar PDF: {str(e)}")


def inserir_assinatura_imagem(arquivo_imagem, assinatura_imagem, posicao_x, posicao_y):
    """
    Insere uma assinatura em uma imagem (JPG, PNG)
    
    Args:
        arquivo_imagem: FileField ou caminho do arquivo de imagem
        assinatura_imagem: ImageField ou caminho da imagem da assinatura
        posicao_x: Posição X no documento
        posicao_y: Posição Y no documento
    
    Returns:
        BytesIO com a imagem modificada
    """
    # Ler a imagem original
    if hasattr(arquivo_imagem, 'read'):
        original_image = Image.open(arquivo_imagem)
        arquivo_imagem.seek(0)
    else:
        original_image = Image.open(arquivo_imagem)
    
    # Converter para RGBA se necessário
    if original_image.mode != 'RGBA':
        original_image = original_image.convert('RGBA')
    
    # Ler a assinatura
    if hasattr(assinatura_imagem, 'read'):
        signature_image = Image.open(assinatura_imagem)
        assinatura_imagem.seek(0)
    else:
        signature_image = Image.open(assinatura_imagem)
    
    # Converter assinatura para RGBA
    if signature_image.mode != 'RGBA':
        signature_image = signature_image.convert('RGBA')
    
    # Redimensionar assinatura se necessário (máximo 200x100)
    max_width, max_height = 200, 100
    if signature_image.width > max_width or signature_image.height > max_height:
        signature_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Criar cópia da imagem original
    resultado = original_image.copy()
    
    # Colar a assinatura na posição especificada
    # Converter coordenadas (assumindo que vêm em pixels)
    x = int(posicao_x)
    y = int(posicao_y)
    
    # Garantir que a posição não saia dos limites
    if x + signature_image.width > resultado.width:
        x = resultado.width - signature_image.width
    if y + signature_image.height > resultado.height:
        y = resultado.height - signature_image.height
    
    # Colar a assinatura
    resultado.paste(signature_image, (x, y), signature_image)
    
    # Converter de volta para RGB se necessário
    if original_image.mode == 'RGB':
        resultado = resultado.convert('RGB')
    
    # Salvar em BytesIO
    output = BytesIO()
    formato = original_image.format or 'PNG'
    resultado.save(output, format=formato)
    output.seek(0)
    
    return output


def inserir_assinatura_docx(arquivo_docx, assinatura_imagem, posicao_x, posicao_y):
    """
    Insere uma assinatura em um arquivo DOCX
    Por enquanto, retorna erro informando que precisa de python-docx
    """
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        
        # Ler o documento
        if hasattr(arquivo_docx, 'read'):
            doc = Document(arquivo_docx)
            arquivo_docx.seek(0)
        else:
            doc = Document(arquivo_docx)
        
        # Adicionar a imagem da assinatura
        # Por enquanto, adicionar no final do documento
        paragraph = doc.add_paragraph()
        run = paragraph.add_run()
        
        # Salvar imagem temporariamente
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        if hasattr(assinatura_imagem, 'read'):
            temp_img.write(assinatura_imagem.read())
            assinatura_imagem.seek(0)
        else:
            with open(assinatura_imagem, 'rb') as f:
                temp_img.write(f.read())
        temp_img.close()
        
        run.add_picture(temp_img.name, width=Inches(2))
        
        # Salvar em BytesIO
        output = BytesIO()
        doc.save(output)
        output.seek(0)
        
        # Limpar arquivo temporário
        os.unlink(temp_img.name)
        
        return output
        
    except ImportError:
        raise Exception("python-docx não está instalado. Para assinar arquivos DOCX, instale: pip install python-docx")
    except Exception as e:
        raise Exception(f"Erro ao processar DOCX: {str(e)}")


# ============================================================================
# FUNÇÕES PARA INSERÇÃO DE PARECERES NO DOCUMENTO FÍSICO
# Sistema independente do módulo de assinaturas
# ============================================================================

def calcular_layout_tabela(num_pareceres):
    """
    Calcula o layout da tabela baseado no número de pareceres.
    
    Args:
        num_pareceres: int - número total de pareceres
        
    Returns:
        dict: {'num_colunas': int, 'num_linhas': int}
    """
    if num_pareceres <= 1:
        num_colunas = 1
    elif num_pareceres <= 4:
        num_colunas = 2
    elif num_pareceres <= 9:
        num_colunas = 3
    else:
        num_colunas = 4
    
    num_linhas = (num_pareceres + num_colunas - 1) // num_colunas  # Arredondar para cima
    
    return {
        'num_colunas': num_colunas,
        'num_linhas': num_linhas
    }


def formatar_texto_parecer(parecer):
    """
    Formata o texto de um parecer para inserção no documento.
    
    Args:
        parecer: ParecerExpediente - instância do parecer
        
    Returns:
        str: texto formatado do parecer
    """
    texto = f"{parecer.get_tipo_parecer_display()}\n"
    texto += f"Título: {parecer.titulo}\n"
    texto += f"Parecer de: {parecer.parecerista.get_full_name() or parecer.parecerista.username}\n"
    texto += f"Data: {parecer.data_parecer.strftime('%d/%m/%Y %H:%M')}\n"
    texto += f"Conteúdo:\n{parecer.conteudo}\n"
    
    if parecer.recomendacoes:
        texto += f"Recomendações:\n{parecer.recomendacoes}\n"
    
    if parecer.observacoes:
        texto += f"Observações:\n{parecer.observacoes}\n"
    
    return texto


def inserir_pareceres_pdf(pdf_file, pareceres_list, posicao_x=50, posicao_y=50, pagina=None):
    """
    Insere múltiplos pareceres em um PDF organizados em tabela.
    
    Args:
        pdf_file: arquivo PDF (FileField, ContentFile ou caminho)
        pareceres_list: lista de instâncias ParecerExpediente
        posicao_x: int - posição X (em pontos, padrão: parte inferior esquerda)
        posicao_y: int - posição Y (em pontos, padrão: parte inferior)
        pagina: int - página onde inserir (None = última página)
        
    Returns:
        BytesIO: PDF modificado com pareceres inseridos
    """
    if not PYPDF2_AVAILABLE or not REPORTLAB_AVAILABLE:
        raise Exception("PyPDF2 e reportlab são necessários para inserir pareceres em PDFs.")
    
    if not pareceres_list:
        raise Exception("Lista de pareceres vazia.")
    
    # Ler o arquivo PDF
    if hasattr(pdf_file, 'path'):
        with open(pdf_file.path, 'rb') as f:
            pdf_content = f.read()
    elif hasattr(pdf_file, 'read'):
        pdf_content = pdf_file.read()
        if hasattr(pdf_file, 'seek'):
            pdf_file.seek(0)
    else:
        with open(pdf_file, 'rb') as f:
            pdf_content = f.read()
    
    # Ler PDF original
    pdf_reader = PdfReader(BytesIO(pdf_content))
    
    # Determinar página
    if pagina is None:
        pagina = len(pdf_reader.pages)
    
    if pagina < 1 or pagina > len(pdf_reader.pages):
        pagina = len(pdf_reader.pages)
    
    # Obter tamanho da página
    target_page = pdf_reader.pages[pagina - 1]
    page_width = float(target_page.mediabox.width)
    page_height = float(target_page.mediabox.height)
    
    # Calcular layout da tabela
    layout = calcular_layout_tabela(len(pareceres_list))
    num_colunas = layout['num_colunas']
    num_linhas = layout['num_linhas']
    
    # Calcular dimensões da tabela
    margem = 20  # margem entre células
    largura_total_disponivel = page_width - (posicao_x * 2)
    altura_total_disponivel = page_height - posicao_y - 50  # deixar espaço inferior
    
    largura_celula = (largura_total_disponivel - (margem * (num_colunas - 1))) / num_colunas
    
    # Criar PDF temporário com a tabela de pareceres
    pareceres_pdf = BytesIO()
    c = canvas.Canvas(pareceres_pdf, pagesize=(page_width, page_height))
    
    # Configurar fonte
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Table, TableStyle, Paragraph, Spacer
    
    styles = getSampleStyleSheet()
    estilo_parecer = ParagraphStyle(
        'ParecerStyle',
        parent=styles['Normal'],
        fontSize=8,
        leading=12,  # Aumentado para melhor espaçamento entre linhas
        textColor=colors.black,
        spaceAfter=3,
        spaceBefore=3,
        fontName='Helvetica',
        allowWidows=1,
        allowOrphans=1
    )
    
    # Preparar dados da tabela e calcular alturas dinâmicas
    # Organizar pareceres em células (cada célula é um Paragraph com todo o texto)
    celulas = []
    alturas_celulas = []  # Armazenar altura de cada célula
    
    for parecer in pareceres_list:
        texto_parecer = formatar_texto_parecer(parecer)
        # Converter quebras de linha \n para <br/> do ReportLab
        # Escapar HTML especial e garantir que as quebras sejam respeitadas
        texto_escaped = texto_parecer.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        texto_html = texto_escaped.replace('\n', '<br/>')
        # Criar um único Paragraph com todo o texto (com quebras de linha HTML)
        paragrafo = Paragraph(texto_html, estilo_parecer)
        celulas.append(paragrafo)
        
        # Calcular altura necessária para este texto
        # Estimar altura baseada no número de linhas e padding
        linhas_texto = len([l for l in texto_parecer.split('\n') if l.strip()])
        altura_estimada = (linhas_texto * estilo_parecer.leading) + 12  # 12 é padding interno
        alturas_celulas.append(max(50, altura_estimada))  # Altura mínima de 50 pontos
    
    # Preencher células vazias se necessário
    total_celulas = num_colunas * num_linhas
    while len(celulas) < total_celulas:
        celulas.append(Paragraph('', estilo_parecer))
        alturas_celulas.append(50)  # Altura mínima para células vazias
    
    # Reorganizar dados em linhas e colunas para a tabela
    dados_tabela_formatada = []
    alturas_linhas = []  # Altura de cada linha (será a maior altura das células na linha)
    
    for i in range(num_linhas):
        linha = []
        altura_linha = 50  # Altura mínima
        
        for j in range(num_colunas):
            idx = i * num_colunas + j
            if idx < len(celulas):
                linha.append(celulas[idx])
                # A altura da linha será a maior altura das células nessa linha
                if idx < len(alturas_celulas):
                    altura_linha = max(altura_linha, alturas_celulas[idx])
            else:
                linha.append(Paragraph('', estilo_parecer))
        
        dados_tabela_formatada.append(linha)
        alturas_linhas.append(altura_linha)
    
    # Criar tabela com alturas dinâmicas
    tabela = Table(dados_tabela_formatada, colWidths=[largura_celula] * num_colunas, rowHeights=alturas_linhas)
    
    # Estilizar tabela
    estilo_tabela = TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('BOX', (0, 0), (-1, -1), 1, colors.black),
    ])
    
    tabela.setStyle(estilo_tabela)
    
    # Calcular posição Y (ReportLab usa origem no canto inferior esquerdo)
    # Calcular altura total da tabela (soma das alturas das linhas)
    altura_total_tabela = sum(alturas_linhas) + (margem * (num_linhas - 1)) if num_linhas > 1 else sum(alturas_linhas)
    y_posicao = page_height - posicao_y - altura_total_tabela
    if y_posicao < 0:
        y_posicao = 50  # Posição mínima
    
    # Desenhar tabela no canvas
    tabela.wrapOn(c, page_width, page_height)
    tabela.drawOn(c, posicao_x, y_posicao)
    
    c.save()
    pareceres_pdf.seek(0)
    
    # Mesclar com PDF original
    pareceres_reader = PdfReader(pareceres_pdf)
    pdf_writer = PdfWriter()
    
    for i, page in enumerate(pdf_reader.pages):
        if i == (pagina - 1):
            # Mesclar página dos pareceres com a página original
            parecer_page = pareceres_reader.pages[0]
            page.merge_page(parecer_page)
        pdf_writer.add_page(page)
    
    # Criar PDF final
    output = BytesIO()
    pdf_writer.write(output)
    output.seek(0)
    
    return output


def inserir_pareceres_imagem(imagem_file, pareceres_list, posicao_x=50, posicao_y=50):
    """
    Insere múltiplos pareceres em uma imagem organizados em tabela.
    
    Args:
        imagem_file: arquivo de imagem (FileField, ContentFile ou caminho)
        pareceres_list: lista de instâncias ParecerExpediente
        posicao_x: int - posição X (em pixels)
        posicao_y: int - posição Y (em pixels, do topo)
        
    Returns:
        BytesIO: imagem modificada com pareceres inseridos
    """
    if not pareceres_list:
        raise Exception("Lista de pareceres vazia.")
    
    # Ler imagem
    if hasattr(imagem_file, 'path'):
        img = Image.open(imagem_file.path)
    elif hasattr(imagem_file, 'read'):
        imagem_file.seek(0)
        img = Image.open(BytesIO(imagem_file.read()))
    else:
        img = Image.open(imagem_file)
    
    # Converter para RGB se necessário
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Calcular layout da tabela
    layout = calcular_layout_tabela(len(pareceres_list))
    num_colunas = layout['num_colunas']
    num_linhas = layout['num_linhas']
    
    # Calcular dimensões
    largura_img, altura_img = img.size
    margem = 10
    largura_disponivel = largura_img - posicao_x - 50
    altura_disponivel = altura_img - posicao_y - 50
    
    largura_celula = (largura_disponivel - (margem * (num_colunas - 1))) / num_colunas
    
    # Criar imagem para desenhar texto
    from PIL import ImageDraw, ImageFont
    
    draw = ImageDraw.Draw(img)
    
    # Tentar carregar fonte, usar padrão se não disponível
    try:
        font_titulo = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 12)
        font_texto = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
    except:
        font_titulo = ImageFont.load_default()
        font_texto = ImageFont.load_default()
    
    # Calcular alturas dinâmicas para cada célula
    alturas_celulas = []
    for parecer in pareceres_list:
        texto_parecer = formatar_texto_parecer(parecer)
        # Calcular altura necessária baseada no número de linhas
        linhas_texto = len([l for l in texto_parecer.split('\n') if l.strip()])
        altura_estimada = (linhas_texto * 12) + 10  # 12 pixels por linha, 10 de padding
        alturas_celulas.append(max(50, altura_estimada))  # Altura mínima de 50 pixels
    
    # Preencher células vazias se necessário
    total_celulas = num_colunas * num_linhas
    while len(alturas_celulas) < total_celulas:
        alturas_celulas.append(50)
    
    # Calcular alturas de linha (altura máxima das células na linha)
    alturas_linhas = []
    for i in range(num_linhas):
        altura_linha = 50  # Altura mínima
        for j in range(num_colunas):
            idx = i * num_colunas + j
            if idx < len(alturas_celulas):
                altura_linha = max(altura_linha, alturas_celulas[idx])
        alturas_linhas.append(altura_linha)
    
    # Desenhar cada parecer em sua célula com altura dinâmica
    y_atual = posicao_y  # Posição Y atual (começa do topo)
    
    for idx, parecer in enumerate(pareceres_list):
        linha = idx // num_colunas
        coluna = idx % num_colunas
        
        # Calcular Y da célula baseado nas alturas anteriores das linhas
        y_celula = y_atual
        for i in range(linha):
            y_celula += alturas_linhas[i] + margem
        
        x_celula = posicao_x + coluna * (largura_celula + margem)
        altura_celula_atual = alturas_celulas[idx]
        
        # Desenhar borda da célula
        draw.rectangle(
            [(x_celula, y_celula), (x_celula + largura_celula, y_celula + altura_celula_atual)],
            outline=(0, 0, 0),
            width=2
        )
        
        # Desenhar texto do parecer
        texto_parecer = formatar_texto_parecer(parecer)
        y_texto = y_celula + 5
        
        # Desenhar cada linha separadamente para respeitar quebras de linha
        for linha_texto in texto_parecer.split('\n'):
            if linha_texto.strip():  # Desenhar apenas linhas não vazias
                if y_texto < y_celula + altura_celula_atual - 15:
                    draw.text((x_celula + 5, y_texto), linha_texto.strip(), fill=(0, 0, 0), font=font_texto)
                    y_texto += 14  # Espaçamento entre linhas
            else:
                # Linha vazia - adicionar espaçamento mínimo
                y_texto += 4
    
    # Salvar imagem
    output = BytesIO()
    img.save(output, format='PNG')
    output.seek(0)
    
    return output


def inserir_pareceres_docx(docx_file, pareceres_list, posicao_x=50, posicao_y=50):
    """
    Insere múltiplos pareceres em um documento Word organizados em tabela.
    
    Args:
        docx_file: arquivo DOCX (FileField, ContentFile ou caminho)
        pareceres_list: lista de instâncias ParecerExpediente
        posicao_x: int - posição X (não usado, pareceres são adicionados no final)
        posicao_y: int - posição Y (não usado)
        
    Returns:
        BytesIO: documento Word modificado com pareceres inseridos
    """
    try:
        from docx import Document
        from docx.shared import Inches, Pt
        from docx.enum.text import WD_ALIGN_PARAGRAPH
    except ImportError:
        raise Exception("python-docx não está instalado. Para inserir pareceres em DOCX, instale: pip install python-docx")
    
    if not pareceres_list:
        raise Exception("Lista de pareceres vazia.")
    
    # Ler documento
    if hasattr(docx_file, 'path'):
        doc = Document(docx_file.path)
    elif hasattr(docx_file, 'read'):
        docx_file.seek(0)
        doc = Document(BytesIO(docx_file.read()))
    else:
        doc = Document(docx_file)
    
    # Adicionar título
    doc.add_heading('Pareceres', 1)
    
    # Calcular layout da tabela
    layout = calcular_layout_tabela(len(pareceres_list))
    num_colunas = layout['num_colunas']
    num_linhas = layout['num_linhas']
    
    # Criar tabela
    tabela = doc.add_table(rows=num_linhas, cols=num_colunas)
    tabela.style = 'Light Grid Accent 1'
    
    # Preencher células
    for idx, parecer in enumerate(pareceres_list):
        linha = idx // num_colunas
        coluna = idx % num_colunas
        
        if linha < num_linhas and coluna < num_colunas:
            celula = tabela.rows[linha].cells[coluna]
            
            # Limpar célula
            celula.text = ''
            
            # Adicionar conteúdo do parecer
            texto_parecer = formatar_texto_parecer(parecer)
            
            # Limpar parágrafo padrão e adicionar cada linha como parágrafo separado
            celula.text = ''
            
            # Adicionar cada linha do parecer como um parágrafo separado
            for linha_texto in texto_parecer.split('\n'):
                if linha_texto.strip():
                    paragrafo = celula.add_paragraph(linha_texto.strip())
                    paragrafo.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    for run in paragrafo.runs:
                        run.font.size = Pt(9)
                elif linha_texto == '':
                    # Adicionar parágrafo vazio para espaçamento
                    celula.add_paragraph()
    
    # Salvar documento
    output = BytesIO()
    doc.save(output)
    output.seek(0)
    
    return output

