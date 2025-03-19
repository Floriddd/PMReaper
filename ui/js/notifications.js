


function showToast(message, type = 'info', duration = 3000) {
    const toastContainer = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icon = getToastIcon(type);
    
    toast.innerHTML = `
        <div class="toast-icon">${icon}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close">×</button>
    `;
    
    
    toastContainer.appendChild(toast);
    
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    
    const timeoutId = setTimeout(() => {
        closeToast(toast);
    }, duration);
    
    
    const closeButton = toast.querySelector('.toast-close');
    closeButton.addEventListener('click', () => {
        clearTimeout(timeoutId);
        closeToast(toast);
    });
}


function closeToast(toastElement) {
    toastElement.classList.remove('show');
    toastElement.classList.add('hide');
    
    
    setTimeout(() => {
        toastElement.remove();
    }, 300);
}


function getToastIcon(type) {
    switch (type) {
        case 'success':
            return `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>`;
        case 'error':
            return `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="15" y1="9" x2="9" y2="15"></line>
                <line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>`;
        case 'warning':
            return `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
            </svg>`;
        case 'info':
        default:
            return `<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>`;
    }
}


function showConfirmModal(title, message, onConfirm, onCancel = () => {}) {
    const modal = document.getElementById('confirmModal');
    const titleEl = document.getElementById('confirmTitle');
    const messageEl = document.getElementById('confirmMessage');
    const yesButton = document.getElementById('confirmYes');
    const noButton = document.getElementById('confirmNo');
    
    
    titleEl.textContent = title;
    messageEl.textContent = message;
    
    
    const newYesButton = yesButton.cloneNode(true);
    const newNoButton = noButton.cloneNode(true);
    yesButton.parentNode.replaceChild(newYesButton, yesButton);
    noButton.parentNode.replaceChild(newNoButton, noButton);
    
    
    newYesButton.addEventListener('click', () => {
        modal.classList.add('hidden');
        onConfirm();
    });
    
    newNoButton.addEventListener('click', () => {
        modal.classList.add('hidden');
        onCancel();
    });
    
    
    modal.classList.remove('hidden');
}


document.addEventListener('DOMContentLoaded', () => {
    
    if (!document.querySelector('#notifications-css')) {
        const css = document.createElement('style');
        css.id = 'notifications-css';
        css.textContent = `
            .toast-container {
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 9999;
                display: flex;
                flex-direction: column;
                gap: 10px;
            }
            
            .toast {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                background-color: var(--bg-secondary);
                border-radius: var(--radius-md);
                box-shadow: var(--shadow-lg);
                max-width: 350px;
                transform: translateX(120%);
                transition: transform 0.3s ease;
                border-left: 4px solid var(--accent-primary);
            }
            
            .toast.show {
                transform: translateX(0);
            }
            
            .toast.hide {
                transform: translateX(120%);
            }
            
            .toast-success {
                border-left-color: var(--success);
            }
            
            .toast-error {
                border-left-color: var(--danger);
            }
            
            .toast-warning {
                border-left-color: var(--warning);
            }
            
            .toast-info {
                border-left-color: var(--info);
            }
            
            .toast-icon {
                margin-right: 12px;
                color: var(--text-primary);
            }
            
            .toast-success .toast-icon {
                color: var(--success);
            }
            
            .toast-error .toast-icon {
                color: var(--danger);
            }
            
            .toast-warning .toast-icon {
                color: var(--warning);
            }
            
            .toast-info .toast-icon {
                color: var(--info);
            }
            
            .toast-message {
                flex: 1;
                font-size: 14px;
            }
            
            .toast-close {
                background: none;
                border: none;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                margin-left: 8px;
                color: var(--text-muted);
                transition: color 0.2s ease;
            }
            
            .toast-close:hover {
                color: var(--text-primary);
            }
            
            .modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: rgba(0, 0, 0, 0.5);
                z-index: 1000;
                opacity: 1;
                transition: opacity 0.3s ease;
            }
            
            .modal.hidden {
                display: none;
                opacity: 0;
            }
            
            .modal-content {
                background-color: var(--bg-secondary);
                border-radius: var(--radius-lg);
                box-shadow: var(--shadow-lg);
                width: 500px;
                max-width: 90%;
                max-height: 80vh;
                overflow: auto;
                transform: scale(1);
                transition: transform 0.3s ease;
            }
            
            .modal-sm {
                width: 400px;
            }
            
            .modal-header {
                padding: 16px;
                border-bottom: 1px solid var(--border-subtle);
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .modal-body {
                padding: 16px;
            }
            
            .modal-footer {
                padding: 16px;
                border-top: 1px solid var(--border-subtle);
                display: flex;
                justify-content: flex-end;
                gap: 8px;
            }
            
            .modal-close {
                background: none;
                border: none;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                color: var(--text-muted);
                transition: color 0.2s ease;
            }
            
            .modal-close:hover {
                color: var(--text-primary);
            }
            
            .settings-group {
                margin-bottom: 24px;
            }
            
            .settings-item {
                margin-bottom: 16px;
            }
            
            .settings-item label {
                display: block;
                margin-bottom: 8px;
                font-weight: 500;
            }
            
            select {
                background-color: var(--bg-tertiary);
                color: var(--text-primary);
                border: 1px solid var(--border-subtle);
                border-radius: var(--radius-sm);
                padding: 8px 12px;
                font-size: 14px;
                width: 100%;
                transition: all var(--transition-fast);
            }
            
            select:focus {
                outline: none;
                border-color: var(--accent-primary);
                box-shadow: 0 0 0 2px rgba(110, 86, 207, 0.2);
            }
        `;
        document.head.appendChild(css);
    }
}); 
