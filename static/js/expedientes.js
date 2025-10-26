// Script para sistema de expedientes

// Remover alertas vazios ou genéricos ao carregar a página
document.addEventListener('DOMContentLoaded', function() {
    // Remover alertas que contenham apenas "O que acontecerá:" sem conteúdo
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        const text = alert.textContent.trim();
        // Verificar se o alerta está vazio ou contém apenas texto genérico
        if (text === 'O que acontecerá:' || text === '' || text.length < 10) {
            alert.remove();
        }
    });
});

