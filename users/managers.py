from django.contrib.auth.models import BaseUserManager
from django.utils import timezone


class UserManager(BaseUserManager):
    """
    Manager customizado para o modelo User que usa email como campo de autenticação.
    """
    
    def create_user(self, email, password=None, **extra_fields):
        """
        Cria e salva um User com email e password fornecidos.
        """
        if not email:
            raise ValueError('O campo Email é obrigatório')
        
        email = self.normalize_email(email)
        
        # Define username como email se não fornecido
        if 'username' not in extra_fields:
            extra_fields['username'] = email
            
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """
        Cria e salva um superuser com email e password fornecidos.
        """
        # Define valores padrão para superuser
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('ativo', True)
        extra_fields.setdefault('tipo_utilizador', 'admin')
        
        # Define username como email se não fornecido
        if 'username' not in extra_fields:
            extra_fields['username'] = email
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser deve ter is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser deve ter is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)
    
    def get_by_natural_key(self, username):
        """
        Permite login por email.
        """
        return self.get(email=username)