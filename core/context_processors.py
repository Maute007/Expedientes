from django.contrib.auth.models import User
from .models import Notificacao


def notificacoes_contexto(request):
    """
    Context processor para adicionar informações de notificações ao contexto global.
    
    Adiciona ao contexto:
    - total_nao_lidas: número de notificações não lidas
    - notificacoes_recentes: últimas 5 notificações do utilizador
    """
    if request.user.is_authenticated:
        try:
            # Contar notificações não lidas
            total_nao_lidas = Notificacao.objects.filter(
                destinatario=request.user, 
                lida=False
            ).count()
            
            # Obter notificações recentes NÃO LIDAS (últimas 5)
            notificacoes_recentes = Notificacao.objects.filter(
                destinatario=request.user,
                lida=False
            ).order_by('-data_criacao')[:5]
            
            return {
                'total_nao_lidas': total_nao_lidas,
                'notificacoes_recentes': notificacoes_recentes
            }
            
        except Exception as e:
            # Em caso de erro, retornar valores padrão
            return {
                'total_nao_lidas': 0,
                'notificacoes_recentes': []
            }
    else:
        # Utilizador não autenticado
        return {
            'total_nao_lidas': 0,
            'notificacoes_recentes': []
        }


def perfil_utilizador_contexto(request):
    """
    Context processor para adicionar informações do perfil do utilizador ao contexto global.
    
    Adiciona ao contexto:
    - perfil: perfil do utilizador (se existir)
    - sector_atual: sector atual do utilizador
    - eh_pca: se o utilizador é PCA
    - eh_chefe: se o utilizador é chefe do sector atual
    """
    if request.user.is_authenticated:
        try:
            # Obter perfil do utilizador (assumindo que existe um modelo PerfilUtilizador)
            perfil = None
            if hasattr(request.user, 'perfil'):
                perfil = request.user.perfil
            
            # Obter sector atual
            sector_atual = request.user.sector_atual
            
            # Verificar se é PCA
            eh_pca = request.user.is_pca
            
            # Verificar se é chefe do sector atual
            eh_chefe = False
            if sector_atual:
                eh_chefe = sector_atual.eh_chefe(request.user)
            
            return {
                'perfil': perfil,
                'sector_atual': sector_atual,
                'eh_pca': eh_pca,
                'eh_chefe': eh_chefe
            }
            
        except Exception as e:
            # Em caso de erro, retornar valores padrão
            return {
                'perfil': None,
                'sector_atual': None,
                'eh_pca': False,
                'eh_chefe': False
            }
    else:
        # Utilizador não autenticado
        return {
            'perfil': None,
            'sector_atual': None,
            'eh_pca': False,
            'eh_chefe': False
        }


def estados_documento_contexto(request):
    """
    Context processor para adicionar estados de documento ao contexto global.
    
    Adiciona ao contexto:
    - estados_documento: todos os estados ativos de documento
    - estados_que_requerem_acao: estados que requerem ação do utilizador
    """
    try:
        from .models import EstadoDocumento
        
        # Obter todos os estados ativos
        estados_documento = EstadoDocumento.objects.filter(ativo=True).order_by('ordem')
        
        # Obter estados que requerem ação
        estados_que_requerem_acao = estados_documento.filter(requer_acao=True)
        
        return {
            'estados_documento': estados_documento,
            'estados_que_requerem_acao': estados_que_requerem_acao
        }
        
    except Exception as e:
        # Em caso de erro, retornar valores padrão
        return {
            'estados_documento': [],
            'estados_que_requerem_acao': []
        }


def sectores_contexto(request):
    """
    Context processor para adicionar informações de sectores ao contexto global.
    
    Adiciona ao contexto:
    - sectores_ativos: todos os sectores ativos
    - sectores_com_chefe_ativo: sectores com chefe ativo
    """
    try:
        from .models import Sector
        
        # Obter todos os sectores ativos
        sectores_ativos = Sector.objects.filter(ativo=True).order_by('nome')
        
        # Obter sectores com chefe ativo
        sectores_com_chefe_ativo = sectores_ativos.filter(chefe__is_active=True)
        
        return {
            'sectores_ativos': sectores_ativos,
            'sectores_com_chefe_ativo': sectores_com_chefe_ativo
        }
        
    except Exception as e:
        # Em caso de erro, retornar valores padrão
        return {
            'sectores_ativos': [],
            'sectores_com_chefe_ativo': []
        }


def configuracoes_sistema_contexto(request):
    """
    Context processor para adicionar configurações do sistema ao contexto global.
    
    Adiciona ao contexto:
    - configuracao_sistema: configurações importantes do sistema
    """
    try:
        from .models import ConfiguracaoSistema
        
        # Obter configurações importantes
        configuracoes_importantes = [
            'nome_sistema',
            'tamanho_maximo_arquivo',
            'timeout_sessao',
            'email_notificacoes',
            'frequencia_notificacoes'
        ]
        
        configuracao_sistema = {}
        for chave in configuracoes_importantes:
            try:
                config = ConfiguracaoSistema.objects.get(chave=chave)
                configuracao_sistema[chave] = config.obter_valor()
            except ConfiguracaoSistema.DoesNotExist:
                configuracao_sistema[chave] = None
        
        return {
            'configuracao_sistema': configuracao_sistema
        }
        
    except Exception as e:
        # Em caso de erro, retornar valores padrão
        return {
            'configuracao_sistema': {}
        }


def hierarquia_utilizador_contexto(request):
    """
    Context processor para adicionar informações de hierarquia do utilizador ao contexto global.
    
    Adiciona ao contexto:
    - nivel_hierarquia: nível hierárquico do utilizador (0=PCA, 1=Chefe, 2=Colaborador)
    - pode_gerir_sectores: se pode gerir sectores
    - pode_criar_despachos: se pode criar despachos/pareceres
    """
    if request.user.is_authenticated:
        try:
            from .permissions import (
                get_user_hierarchy_level, 
                is_pca_or_chefe, 
                can_create_despacho
            )
            
            # Obter nível hierárquico
            nivel_hierarquia = get_user_hierarchy_level(request.user)
            
            # Verificar se pode gerir sectores
            pode_gerir_sectores = is_pca_or_chefe(request.user)
            
            # Verificar se pode criar despachos
            pode_criar_despachos = can_create_despacho(request.user, 'despacho')
            
            return {
                'nivel_hierarquia': nivel_hierarquia,
                'pode_gerir_sectores': pode_gerir_sectores,
                'pode_criar_despachos': pode_criar_despachos
            }
            
        except Exception as e:
            # Em caso de erro, retornar valores padrão
            return {
                'nivel_hierarquia': 2,
                'pode_gerir_sectores': False,
                'pode_criar_despachos': False
            }
    else:
        # Utilizador não autenticado
        return {
            'nivel_hierarquia': -1,
            'pode_gerir_sectores': False,
            'pode_criar_despachos': False
        }


def estatisticas_documentos_contexto(request):
    """
    Context processor para adicionar estatísticas de documentos ao contexto global.
    Aplica as mesmas regras de filtro que os dashboards para cada tipo de utilizador.
    
    Adiciona ao contexto:
    - total_processadas: número de documentos processados (filtrado por utilizador)
    - total_enviadas: número de documentos enviados (filtrado por utilizador)
    - total_pendentes: número de documentos pendentes (filtrado por utilizador)
    """
    if request.user.is_authenticated:
        try:
            from entrada.models import Expediente
            from .models import EstadoDocumento
            from django.db.models import Q
            
            # Obter estados específicos baseados nos fixtures
            # Processadas: Concluído + Arquivado (documentos finalizados)
            estados_processadas = EstadoDocumento.objects.filter(nome__in=['Concluído', 'Arquivado'])
            # Enviadas: Encaminhado (documentos em circulação)
            estado_enviado = EstadoDocumento.objects.filter(nome='Encaminhado').first()
            # Pendentes: Recebido + Em Tratamento + Devolvido (documentos aguardando ação)
            estados_pendentes = EstadoDocumento.objects.filter(nome__in=['Recebido', 'Em Tratamento', 'Devolvido'])
            
            # Aplicar filtros baseados no tipo de utilizador (mesma lógica dos dashboards)
            if request.user.tipo_utilizador == 'secretaria':
                # Secretaria vê todos os expedientes
                queryset = Expediente.objects.filter(ativo=True)
            else:
                # Outros utilizadores veem expedientes direcionados a eles OU onde estão envolvidos
                queryset = Expediente.objects.filter(
                    Q(utilizador_atual=request.user) |  # Documentos atuais
                    Q(membros_envolvidos=request.user)  # Documentos onde está envolvido
                ).distinct()
            
            # Contar documentos por estado usando o queryset filtrado
            total_processadas = queryset.filter(estado_atual__in=estados_processadas).count() if estados_processadas.exists() else 0
            total_enviadas = queryset.filter(estado_atual=estado_enviado).count() if estado_enviado else 0
            total_pendentes = queryset.filter(estado_atual__in=estados_pendentes).count() if estados_pendentes.exists() else 0
            
            return {
                'total_processadas': total_processadas,
                'total_enviadas': total_enviadas,
                'total_pendentes': total_pendentes
            }
            
        except Exception as e:
            # Em caso de erro, retornar valores padrão
            return {
                'total_processadas': 0,
                'total_enviadas': 0,
                'total_pendentes': 0
            }
    else:
        # Utilizador não autenticado
        return {
            'total_processadas': 0,
            'total_enviadas': 0,
            'total_pendentes': 0
        }


def estados_workflow_contexto(request):
    """
    Context processor para adicionar mapeamento de estados e ações de workflow.
    
    Adiciona ao contexto:
    - mapa_estados_acoes: dicionário com estados e suas ações disponíveis
    - cores_estados: dicionário com cores dos badges por estado
    """
    try:
        from core.models import EstadoDocumento
        
        # Obter todos os estados ativos
        estados = EstadoDocumento.objects.filter(ativo=True)
        
        # Criar mapa de cores para badges
        cores_estados = {}
        for estado in estados:
            cores_estados[estado.nome] = estado.cor
        
        # Mapeamento de estados para transições permitidas
        # Regras de transição:
        # - tratar → Em Tratamento
        # - encaminhar → Encaminhado  
        # - marcar_recebido → Recebido
        # - concluir → Concluído
        # - arquivar → Arquivado
        # - reabrir → Em Tratamento
        mapa_estados_acoes = {
            'Recebido': ['encaminhar', 'tratar', 'arquivar'],
            'Pendente': ['encaminhar', 'tratar', 'arquivar'],
            'Encaminhado': ['marcar_recebido', 'reencaminhar', 'devolver'],
            'Em Tratamento': ['concluir', 'encaminhar', 'devolver'],
            'Concluído': ['arquivar', 'reabrir'],
            'Arquivado': ['reabrir']  # reabrir → Em Tratamento
        }
        
        return {
            'mapa_estados_acoes': mapa_estados_acoes,
            'cores_estados': cores_estados
        }
        
    except Exception as e:
        return {
            'mapa_estados_acoes': {},
            'cores_estados': {}
        }
