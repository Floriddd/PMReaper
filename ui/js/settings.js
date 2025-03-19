

let currentSettings = {
    theme: 'dark',
    reaperPath: '',
};


function initSettings() {
    loadSettings();
    
    
    document.querySelector('.menu').addEventListener('click', () => {
        openSettingsModal();
    });
    
    
    document.getElementById('themeSelector').addEventListener('change', (e) => {
        const selectedTheme = e.target.value;
        previewTheme(selectedTheme);
    });
}


function loadSettings() {
    try {
        
        if (typeof pyBridge !== 'undefined' && pyBridge && typeof pyBridge.loadSettings === 'function') {
            
            try {
                const settingsJson = pyBridge.loadSettings("callback");
                if (settingsJson) {
                    
                    const parsedSettings = JSON.parse(settingsJson);
                    currentSettings = { ...currentSettings, ...parsedSettings };
                    
                    
                    applyTheme(currentSettings.theme);
                    
                    
                    updateSettingsUI();
                    
                } else {
                }
            } catch (parseError) {
                console.error('Ошибка при загрузке настроек:', parseError);
            }
        } else {
            
            const savedSettings = localStorage.getItem('pmReaperSettings');
            if (savedSettings) {
                currentSettings = { ...currentSettings, ...JSON.parse(savedSettings) };
                
                
                applyTheme(currentSettings.theme);
                
                
                updateSettingsUI();
            }
        }
    } catch (error) {
        console.error('Ошибка при загрузке настроек:', error);
    }
}


function updateSettingsUI() {
    
    const themeSelector = document.getElementById('themeSelector');
    const reaperPath = document.getElementById('reaperPath');
    
    if (themeSelector) {
        themeSelector.value = currentSettings.theme;
    } else {
        console.warn('Элемент themeSelector не найден в DOM при загрузке настроек');
    }
    
    if (reaperPath) {
        reaperPath.value = currentSettings.reaperPath || '';
    } else {
        console.warn('Элемент reaperPath не найден в DOM при загрузке настроек');
    }
}


function saveSettings() {
    try {
        
        const themeSelector = document.getElementById('themeSelector');
        const reaperPath = document.getElementById('reaperPath');
        
        
        if (themeSelector) {
            currentSettings.theme = themeSelector.value;
        } else {
            console.warn('Элемент themeSelector не найден в DOM');
        }
        
        if (reaperPath) {
            currentSettings.reaperPath = reaperPath.value;
        } else {
            console.warn('Элемент reaperPath не найден в DOM');
        }
        
        
        const settingsJson = JSON.stringify(currentSettings);
        
        
        if (typeof pyBridge !== 'undefined' && pyBridge && typeof pyBridge.saveSettings === 'function') {
            try {
                const success = pyBridge.saveSettings(settingsJson);
                
                if (success) {
                    
                    
                    if (typeof showToast === 'function') {
                        showToast('Настройки сохранены', 'success');
                    }
                } else {
                    console.error('Не удалось сохранить настройки в файл');
                    
                    if (typeof showToast === 'function') {
                        showToast('Ошибка при сохранении настроек', 'error');
                    }
                }
            } catch (saveError) {
                console.error('Ошибка при сохранении настроек:', saveError);
                if (typeof showToast === 'function') {
                    showToast('Ошибка при сохранении настроек', 'error');
                }
            }
        } else {
            
            localStorage.setItem('pmReaperSettings', settingsJson);
            
            if (typeof showToast === 'function') {
                showToast('Настройки сохранены (локально)', 'success');
            }
        }
        
        
        applyTheme(currentSettings.theme);
        
        
        closeSettingsModal();
    } catch (error) {
        console.error('Ошибка при сохранении настроек:', error);
        
        if (typeof showToast === 'function') {
            showToast('Ошибка при сохранении настроек', 'error');
        }
    }
}


function applyTheme(theme) {
    if (theme === 'system') {
        
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        theme = prefersDark ? 'dark' : 'light';
    }
    
    document.body.setAttribute('data-theme', theme);
}


function previewTheme(theme) {
    applyTheme(theme);
}


function openSettingsModal() {
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.style.display = 'flex';
        settingsModal.classList.remove('hidden');
    } else {
        console.error("Модальное окно настроек не найдено в DOM");
    }
}


function closeSettingsModal() {
    const settingsModal = document.getElementById('settingsModal');
    if (settingsModal) {
        settingsModal.style.display = 'none';
        settingsModal.classList.add('hidden');
        
        
        applyTheme(currentSettings.theme);
    } else {
        console.error("Модальное окно настроек не найдено в DOM");
    }
}


function browseReaperPath() {
    
    if (typeof pyBridge !== 'undefined' && pyBridge) {
        pyBridge.browseReaperPath((path) => {
            if (path) {
                const reaperPathInput = document.getElementById('reaperPath');
                if (reaperPathInput) {
                    reaperPathInput.value = path;
                }
            }
        });
    } else {
        console.error("Мост к Python (pyBridge) не найден");
    }
}


document.addEventListener('DOMContentLoaded', initSettings); 
