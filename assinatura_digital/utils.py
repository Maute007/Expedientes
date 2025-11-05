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

