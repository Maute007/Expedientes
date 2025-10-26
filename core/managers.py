from django.db import models
from django.contrib.auth.models import User


class BaseManager(models.Manager):
    """
    Manager base com métodos comuns para todos os modelos.
    """
    
    def ativos(self):
        """
        Retorna apenas registros ativos.
        """
        return self.filter(ativo=True)
    
    def por_sector(self, sector):
        """
        Filtra por sector específico.
        """
        if hasattr(self.model, 'sector_atual'):
            return self.filter(sector_atual=sector)
        elif hasattr(self.model, 'sector'):
            return self.filter(sector=sector)
        else:
            return self.none()
    
    def por_utilizador(self, user):
        """
        Filtra por utilizador específico.
        """
        if hasattr(self.model, 'utilizador'):
            return self.filter(utilizador=user)
        elif hasattr(self.model, 'autor'):
            return self.filter(autor=user)
        elif hasattr(self.model, 'destinatario'):
            return self.filter(destinatario=user)
        elif hasattr(self.model, 'remetente'):
            return self.filter(remetente=user)
        else:
            return self.none()
    
    def por_chefe_sector(self, user):
        """
        Filtra registros onde o utilizador é chefe do sector.
        """
        if not user.sector_atual:
            return self.none()
        
        # Verifica se o utilizador é chefe do sector atual
        if not user.sector_atual.eh_chefe(user):
            return self.none()
        
        # Retorna registros do sector onde é chefe
        return self.por_sector(user.sector_atual)
    
    def por_pca(self):
        """
        Filtra registros relacionados ao PCA.
        """
        pca_users = User.objects.filter(is_pca=True)
        if hasattr(self.model, 'utilizador'):
            return self.filter(utilizador__in=pca_users)
        elif hasattr(self.model, 'autor'):
            return self.filter(autor__in=pca_users)
        elif hasattr(self.model, 'destinatario'):
            return self.filter(destinatario__in=pca_users)
        else:
            return self.none()
    
    def recentes(self, dias=30):
        """
        Retorna registros dos últimos N dias.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        data_limite = timezone.now() - timedelta(days=dias)
        
        if hasattr(self.model, 'data_criacao'):
            return self.filter(data_criacao__gte=data_limite)
        elif hasattr(self.model, 'data_atualizacao'):
            return self.filter(data_atualizacao__gte=data_limite)
        else:
            return self.none()
    
    def por_periodo(self, data_inicio, data_fim):
        """
        Filtra registros por período específico.
        """
        if hasattr(self.model, 'data_criacao'):
            return self.filter(data_criacao__range=[data_inicio, data_fim])
        elif hasattr(self.model, 'data_atualizacao'):
            return self.filter(data_atualizacao__range=[data_inicio, data_fim])
        else:
            return self.none()


class EstadoDocumentoManager(BaseManager):
    """
    Manager específico para EstadoDocumento.
    """
    
    def por_ordem(self):
        """
        Retorna estados ordenados por ordem.
        """
        return self.order_by('ordem')
    
    def que_requerem_acao(self):
        """
        Retorna estados que requerem ação do utilizador.
        """
        return self.filter(requer_acao=True)
    
    def proximos_estados(self, estado_atual):
        """
        Retorna próximos estados possíveis baseado no estado atual.
        """
        return self.filter(
            ordem__gt=estado_atual.ordem,
            ativo=True
        ).order_by('ordem')


class NotificacaoManager(BaseManager):
    """
    Manager específico para Notificacao.
    """
    
    def nao_lidas(self, user):
        """
        Retorna notificações não lidas de um utilizador.
        """
        return self.filter(destinatario=user, lida=False)
    
    def por_tipo(self, tipo):
        """
        Filtra por tipo de notificação.
        """
        return self.filter(tipo=tipo)
    
    def urgentes(self):
        """
        Retorna apenas notificações urgentes.
        """
        return self.filter(prioridade='urgente')
    
    def recentes_usuario(self, user, limite=10):
        """
        Retorna notificações recentes de um utilizador.
        """
        return self.filter(destinatario=user).order_by('-data_criacao')[:limite]


class SectorManager(BaseManager):
    """
    Manager específico para Sector.
    """
    
    def com_chefe_ativo(self):
        """
        Retorna sectores com chefe ativo.
        """
        return self.filter(chefe__is_active=True)
    
    def por_chefe(self, user):
        """
        Retorna sectores onde o utilizador é chefe.
        """
        return self.filter(
            models.Q(chefe=user) | models.Q(chefe_substituto=user)
        )
    
    def com_colaboradores(self):
        """
        Retorna sectores que têm colaboradores.
        """
        return self.filter(users__is_active=True).distinct()


class DespachoDocumentoManager(BaseManager):
    """
    Manager específico para DespachoDocumento.
    """
    
    def por_tipo(self, tipo):
        """
        Filtra por tipo de despacho.
        """
        return self.filter(tipo=tipo)
    
    def por_visibilidade(self, visibilidade):
        """
        Filtra por nível de visibilidade.
        """
        return self.filter(visivel_para=visibilidade)
    
    def editaveis_por(self, user):
        """
        Retorna despachos editáveis por um utilizador.
        """
        from django.utils import timezone
        from datetime import timedelta
        
        limite_tempo = timezone.now() - timedelta(days=1)
        
        return self.filter(
            autor=user,
            data_criacao__gte=limite_tempo
        )
    
    def por_documento(self, documento):
        """
        Filtra despachos de um documento específico.
        """
        return self.filter(
            content_type__model=documento._meta.model_name,
            object_id=documento.pk
        )
