


window.currentDropTarget = null;


document.addEventListener('DOMContentLoaded', function() {
    initDragDropHandlers();
});


function initDragDropHandlers() {
    const fileLists = document.querySelectorAll('.file-list');
    
    fileLists.forEach(list => {
        
        list.addEventListener('dragover', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            
            if (e.dataTransfer) {
                e.dataTransfer.dropEffect = "copy";
            }
            
            
            this.classList.add('drop-target');
            
            
            updateCurrentDropTarget(this.id);
        });
        
        
        list.addEventListener('dragenter', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            
            this.classList.add('drop-target');
            
            
            updateCurrentDropTarget(this.id);
        });
        
        
        list.addEventListener('dragleave', function(e) {
            e.preventDefault();
            
            
            const rect = this.getBoundingClientRect();
            const isInElement = (
                e.clientX >= rect.left && 
                e.clientX <= rect.right && 
                e.clientY >= rect.top && 
                e.clientY <= rect.bottom
            );
            
            if (!isInElement) {
                this.classList.remove('drop-target');
                
                
                if (window.currentDropTarget === getDropTargetType(this.id)) {
                    window.currentDropTarget = null;
                }
            }
        });
        
        
        list.addEventListener('drop', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            
            const targetType = getDropTargetType(this.id);
            window.currentDropTarget = targetType;
            
            
            
            this.classList.remove('drop-target');
            
            
            clearDragStyles();
        });
    });
}


function updateCurrentDropTarget(id) {
    const targetType = getDropTargetType(id);
    window.currentDropTarget = targetType;
}


function getDropTargetType(id) {
    const typeMap = {
        'rawsList': 'raws',
        'roadsList': 'roads',
        'voiceList': 'voice',
        'subsList': 'subs'
    };
    
    return typeMap[id] || null;
}


function clearDragStyles() {
    
    document.querySelectorAll('.potential-drop-target').forEach(list => {
        list.classList.remove('potential-drop-target');
    });
    
    
    document.querySelectorAll('.drop-target').forEach(el => {
        el.classList.remove('drop-target');
    });
}


function getCurrentDropTarget() {
    
    if (window.currentDropTarget) {
        return window.currentDropTarget;
    }
    
    
    const dropTarget = document.querySelector('.file-list.drop-target');
    if (dropTarget) {
        const targetType = getDropTargetType(dropTarget.id);
        return targetType;
    }
    
    return null;
}


function dragEnterUI() {
    document.body.classList.add('dragging');
    
    
    document.querySelectorAll('.file-list').forEach(list => {
        list.classList.add('potential-drop-target');
    });
}


function dragLeaveUI() {
    document.body.classList.remove('dragging');
    
    
    clearDragStyles();
    
    
    window.currentDropTarget = null;
}


function updateContainerSizes() {
    
    
    const ITEM_HEIGHT = 36; 
    const ITEM_MARGIN = 4;  
    const MIN_HEIGHT = 60;  
    const PADDING = 8;      
    
    
    const fileLists = ['rawsList', 'roadsList', 'voiceList', 'subsList'];
    
    fileLists.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            
            const fileCount = element.children.length;
            
            
            
            
            const exactHeight = fileCount > 0 
                ? (fileCount * ITEM_HEIGHT) + ((fileCount - 1) * ITEM_MARGIN) + (PADDING * 2)
                : MIN_HEIGHT;
                
            
            element.style.height = `${exactHeight}px`;
            element.style.minHeight = `${Math.max(exactHeight, MIN_HEIGHT)}px`;
            
            
            const section = element.closest('.section');
            if (section) {
                
                const counter = section.querySelector('.file-counter');
                if (counter) {
                    counter.textContent = fileCount === 1 ? '1 файл' : 
                                         (fileCount > 1 && fileCount < 5) ? `${fileCount} файла` : 
                                         `${fileCount} файлов`;
                }
            }
        }
    });
}


window.addEventListener('load', function() {
    
    
    if (typeof initSettings === 'function') {
        initSettings();
    } else {
        console.warn("Функция initSettings не найдена, возможно, файл settings.js не загружен");
    }
    
    
    const fileLists = ['rawsList', 'roadsList', 'voiceList', 'subsList'];
    
    fileLists.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            
            
            const style = window.getComputedStyle(element);
            
            
            element.style.display = 'block';
            element.style.visibility = 'visible';
            element.style.opacity = '1';
            
            
            element.style.maxHeight = 'none';
            
            
            const section = element.closest('.section');
            if (section) {
                section.style.maxHeight = 'none';
                section.style.height = 'auto';
            }
            
            
            element.style.border = '2px solid red';
            
            
            setTimeout(() => {
                element.style.border = '1px solid var(--border-subtle)';
            }, 2000);
        } else {
            console.error(`Список ${id} не найден в DOM!`);
        }
    });
    
    
    initDragDropHandlers();
    
    
    updateContainerSizes();
    
    
    const fileListsObserver = new MutationObserver(updateContainerSizes);
    
    
    fileLists.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            fileListsObserver.observe(element, { 
                childList: true,  
                subtree: false    
            });
        }
    });
    
    
    window.addEventListener('resize', updateContainerSizes);
    
    
    setTimeout(function() {
        const menuButton = document.querySelector('.menu');
        if (menuButton) {
            
            
            menuButton.onclick = function() {
                
                
                const settingsModal = document.getElementById('settingsModal');
                if (settingsModal) {
                    settingsModal.classList.remove('hidden');
                } else {
                    console.error("Модальное окно настроек не найдено в DOM!");
                }
            };
        } else {
            console.warn("Кнопка меню не найдена");
        }
    }, 500); 
}); 
