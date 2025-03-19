


function directMenuFix() {
    
    const menuButton = document.querySelector('.menu');
    
    if (menuButton) {
        
        menuButton.onclick = function(event) {
            
            const settingsModal = document.getElementById('settingsModal');
            if (settingsModal) {                
                
                settingsModal.style.display = 'flex';
                settingsModal.classList.remove('hidden');
            } else {
                console.error("Модальное окно не найдено");
            }
            
            
            if (event) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            return false;
        };
        
        
        menuButton.addEventListener('click', function(event) {
            const settingsModal = document.getElementById('settingsModal');
            if (settingsModal) {
                
                settingsModal.style.display = 'flex';
                settingsModal.classList.remove('hidden');
            }
            
            event.preventDefault();
            event.stopPropagation();
        });
    } else {
        console.error("Кнопка меню не найдена в DOM");
    }
}


window.addEventListener('DOMContentLoaded', function() {
    setTimeout(directMenuFix, 300);
});

window.addEventListener('load', function() {
    directMenuFix();
    setTimeout(directMenuFix, 500);
});


document.addEventListener('click', function(event) {
    const modals = document.querySelectorAll('.modal:not(.hidden)');
    
    modals.forEach(modal => {
        const modalContent = modal.querySelector('.modal-content');
        
        
        if (modalContent && !modalContent.contains(event.target) && modal.contains(event.target)) {
            
            const modalId = modal.id;
            
            if (modalId === 'settingsModal' && typeof closeSettingsModal === 'function') {
                closeSettingsModal();
            } else {
                
                modal.classList.add('hidden');
                modal.style.display = 'none';
            }
        }
    });
}); 
