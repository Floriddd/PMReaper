let currentProject = '';
let baseDir = '';

// Инициализация переменных при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    // Получаем текущий проект и базовую директорию из Python
    pyBridge.getCurrentProject((project) => {
        currentProject = project;
    });
    
    pyBridge.getBaseDir((dir) => {
        baseDir = dir;
    });
});

function updateRightPanel(season, episode) {
    if (!season || !episode || !currentProject) {
        clearRightPanel();
        return;
    }


    
    pyBridge.getFilesByType(currentProject, season, episode, (filesByType) => {
        
        try {
            
            const files = typeof filesByType === 'string' ? JSON.parse(filesByType) : filesByType;
            
            updateFileList('rawsList', files.raws || []);
            updateFileList('roadsList', files.roads || []);
            updateFileList('voiceList', files.voice || []);
            updateFileList('subsList', files.subs || []);
            
            
            updateFileCounter('rawsCounter', files.raws ? files.raws.length : 0);
            updateFileCounter('roadsCounter', files.roads ? files.roads.length : 0);
            updateFileCounter('voiceCounter', files.voice ? files.voice.length : 0);
            updateFileCounter('subsCounter', files.subs ? files.subs.length : 0);
            
        } catch (error) {
            console.error("Ошибка при обработке данных:", error);
        }
    });
}


function updateFileCounter(counterId, count) {
    const counter = document.getElementById(counterId);
    if (counter) {
        const fileWord = getCorrectFileForm(count);
        counter.textContent = `${count} ${fileWord}`;
    }
}


function getCorrectFileForm(count) {
    if (count % 10 === 1 && count % 100 !== 11) {
        return "файл";
    } else if ([2, 3, 4].includes(count % 10) && ![12, 13, 14].includes(count % 100)) {
        return "файла";
    } else {
        return "файлов";
    }
}


function clearRightPanel() {
    ['rawsList', 'roadsList', 'voiceList', 'subsList'].forEach(listId => {
        const list = document.getElementById(listId);
        if (list) {
            list.innerHTML = '';
        }
    });
    
    
    ['rawsCounter', 'roadsCounter', 'voiceCounter', 'subsCounter'].forEach(counterId => {
        updateFileCounter(counterId, 0);
    });
}


function updateFileList(listId, files) {
    const list = document.getElementById(listId);
    if (!list) return;
    
    list.innerHTML = '';
    
    if (files.length === 0) {
        const emptyMessage = document.createElement('li');
        emptyMessage.className = 'empty-message';
        emptyMessage.textContent = 'Нет файлов';
        list.appendChild(emptyMessage);
        return;
    }
    
    files.forEach(filePath => {
        const li = document.createElement('li');
        li.className = 'file-item';
        
        
        const fileName = getDisplayFilename(filePath);
        li.textContent = fileName;
        
        
        li.setAttribute('data-path', filePath);
        li.draggable = true;
        
        
        const extension = getFileExtension(fileName).toLowerCase();
        if (['.mp3', '.wav', '.ogg', '.flac', '.aif', '.aiff', '.m4a', '.wma'].includes(extension)) {
            li.classList.add('audio');
        } else if (['.mp4', '.avi', '.mov', '.mkv', '.wmv'].includes(extension)) {
            li.classList.add('video');
        } else if (['.txt', '.srt', '.ass', '.ssa', '.vtt'].includes(extension)) {
            li.classList.add('text');
        }
        
        
        const listType = listId.replace('List', '');
        li.setAttribute('data-source-type', listType);
        
        
        li.addEventListener('dragstart', handleDragStart);
        li.addEventListener('click', handleFileClick);
        li.addEventListener('contextmenu', handleFileContextMenu);
        
        list.appendChild(li);
    });
}


function getFileExtension(filename) {
    return filename.slice((filename.lastIndexOf(".") - 1 >>> 0) + 1);
}


function getDisplayFilename(path) {
    return path.split('\\').pop().split('/').pop();
}


function handleDragStart(event) {
    const sourceType = event.target.getAttribute('data-source-type');
    event.dataTransfer.setData('text/plain', event.target.getAttribute('data-path'));
    event.dataTransfer.setData('source-type', sourceType);
    event.target.classList.add('dragged');
    
    
    window.currentDraggedElement = event.target;
}


function handleFileClick(event) {
    
    const fileElements = document.querySelectorAll('.file-item');
    fileElements.forEach(el => el.classList.remove('selected'));
    event.target.classList.add('selected');
    
    
    const filePath = event.target.getAttribute('data-path');
    pyBridge.openFile(filePath);
}


function handleFileContextMenu(event) {
    event.preventDefault();
    
    const filePath = event.target.getAttribute('data-path');
    
    
    showFileContextMenu(filePath, event.clientX, event.clientY);
}


function showFileContextMenu(filePath, x, y) {
    
}


function getCurrentProjectPath() {
    if (currentProject && baseDir) {
        return baseDir + '/' + currentProject;
    }
    return '';
}


function allowDrop(event) {
    event.preventDefault();
}


function dragEnter(event) {
    event.preventDefault();
    const target = findDropTarget(event.target);
    if (target) {
        target.classList.add('drop-target');
        
        const section = findParentSection(target);
        if (section) {
            section.classList.add('drop-target-container');
            
            const type = target.id.replace('List', '');
            section.setAttribute('data-highlight-type', type);
        }
    }
}


function dragLeave(event) {
    event.preventDefault();
    const target = findDropTarget(event.target);
    const relatedTarget = event.relatedTarget;
    
    
    if (target && !target.contains(relatedTarget)) {
        target.classList.remove('drop-target');
        
        const section = findParentSection(target);
        if (section) {
            section.classList.remove('drop-target-container');
            section.removeAttribute('data-highlight-type');
        }
    }
}


function dragEnterUI() {
    
    document.body.classList.add('dragging');
}


function dragLeaveUI() {
    
    document.body.classList.remove('dragging');
    
    
    document.querySelectorAll('.drop-target').forEach(el => {
        el.classList.remove('drop-target');
    });
    
    document.querySelectorAll('.drop-target-container').forEach(el => {
        el.classList.remove('drop-target-container');
        el.removeAttribute('data-highlight-type');
    });
    
    
    if (window.currentDraggedElement) {
        window.currentDraggedElement.classList.remove('dragged');
        window.currentDraggedElement = null;
    }
}


function findDropTarget(element) {
    const validIds = ['rawsList', 'roadsList', 'voiceList', 'subsList'];
    
    
    let current = element;
    while (current) {
        if (validIds.includes(current.id)) {
            return current;
        }
        current = current.parentElement;
    }
    
    return null;
}


function findParentSection(element) {
    let current = element;
    while (current) {
        if (current.classList.contains('section')) {
            return current;
        }
        current = current.parentElement;
    }
    
    return null;
}


function drop(event, targetType) {
    event.preventDefault();
    
    
    document.querySelectorAll('.drop-target').forEach(el => {
        el.classList.remove('drop-target');
    });
    
    
    document.querySelectorAll('.drop-target-container').forEach(el => {
        el.classList.remove('drop-target-container');
        el.removeAttribute('data-highlight-type');
    });
    
    
    const filePath = event.dataTransfer.getData('text/plain');
    const sourceType = event.dataTransfer.getData('source-type');
    
    
    if (filePath) {
        
        if (sourceType !== targetType) {
            
            
            if (currentProject && currentSeason && currentEpisode) {
                
                pyBridge.moveFile(filePath, targetType, currentProject, currentSeason, currentEpisode, (result) => {
                    if (result === "success") {
                        
                        updateRightPanel(currentSeason, currentEpisode);
                        showToast(`Файл перемещен в ${getTypeName(targetType)}`, 'success');
                    } else {
                        showToast('Не удалось переместить файл', 'error');
                        console.error('Ошибка при перемещении файла:', result);
                    }
                });
            } else {
                showToast('Выберите проект, сезон и эпизод', 'warning');
            }
        } else {
            
        }
    } else {
        
        
    }
}


function getTypeName(type) {
    const typeNames = {
        'raws': 'Равки',
        'roads': 'Делённые дороги',
        'voice': 'Озвучка',
        'subs': 'Субтитры'
    };
    
    return typeNames[type] || type;
}


function openFolderForType(type) {
    if (!currentProject || !currentSeason || !currentEpisode) {
        showToast('Сначала выберите проект, сезон и эпизод', 'warning');
        return;
    }
    
    const folderMapping = {
        'raws': 'raws',
        'roads': 'outs',
        'voice': 'source',
        'subs': 'subs'
    };
    
    const folderName = folderMapping[type] || type;
    const seasonFolder = `S${String(currentSeason).padStart(2, '0')}`;
    const episodeFolder = `${seasonFolder}-E${String(currentEpisode).padStart(2, '0')}`;
    const path = `${baseDir}/${currentProject}/${seasonFolder}/${episodeFolder}/${folderName}`;
    
    pyBridge.openFolder(path);
}

function showSection(sectionId) {
    document.getElementById("projectListSection").classList.add("hidden");
    document.getElementById("projectDetailSection").classList.add("hidden");
    document.getElementById("selectProjectDirSection").classList.add("hidden");
    document.getElementById(sectionId).classList.remove("hidden");
}
