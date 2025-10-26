from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.contrib import messages

User = get_user_model()

def test_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember_me', False)
        
        print(f"Login attempt: {username}")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.get_full_name()}!')
                
                # Redirecionar baseado no tipo de utilizador
                if user.is_superuser or user.tipo_utilizador == 'admin':
                    return HttpResponseRedirect('/dashboard/admin/')
                elif user.tipo_utilizador == 'pca':
                    return HttpResponseRedirect('/dashboard/pca/')
                elif user.tipo_utilizador == 'secretaria':
                    return HttpResponseRedirect('/dashboard/secretaria/')
                elif user.tipo_utilizador == 'chefe':
                    return HttpResponseRedirect('/dashboard/chefe/')
                elif user.tipo_utilizador == 'externo':
                    return HttpResponseRedirect('/dashboard/externo/')
                else:  # colaborador ou outro
                    return HttpResponseRedirect('/dashboard/colaborador/')
            else:
                messages.error(request, 'Conta desativada. Contacte o administrador.')
        else:
            messages.error(request, 'Email ou senha incorretos.')
    
    return render(request, 'users/login_simple.html')
