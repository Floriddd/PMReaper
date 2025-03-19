

var selectedEpisodeLi = null;


window.currentDropTarget = null;

function selectEpisode(season, episode, liElement) {
    if (selectedEpisodeLi && selectedEpisodeLi !== liElement) {
        selectedEpisodeLi.classList.remove('selected');
    }
    liElement.classList.add('selected');
    selectedEpisodeLi = liElement;

    currentSeason = season;
    currentEpisode = episode;
    pyBridge.setCurrentSeasonEpisode(season, episode);

    updateRightPanel(season, episode);
}

function updateRightPanel(season, episode) {
    if (!season || !episode || !currentProject) {
        return;
    }
    
    
    
    pyBridge.getFilesByType(currentProject, season, episode, function(filesByType) {
        
        try {
            
            const files = typeof filesByType === 'string' ? JSON.parse(filesByType) : filesByType;
            
            
            updateFileList('rawsList', files.raws || [], 'raws');
            updateFileList('roadsList', files.roads || [], 'roads');
            updateFileList('voiceList', files.voice || [], 'voice');
            updateFileList('subsList', files.subs || [], 'subs');
            
            
            const rawsCounter = document.getElementById('rawsCounter');
            if (rawsCounter) rawsCounter.textContent = `${files.raws ? files.raws.length : 0} файлов`;
            
            const roadsCounter = document.getElementById('roadsCounter');
            if (roadsCounter) roadsCounter.textContent = `${files.roads ? files.roads.length : 0} файлов`;
            
            const voiceCounter = document.getElementById('voiceCounter');
            if (voiceCounter) voiceCounter.textContent = `${files.voice ? files.voice.length : 0} файлов`;
            
            const subsCounter = document.getElementById('subsCounter');
            if (subsCounter) subsCounter.textContent = `${files.subs ? files.subs.length : 0} файлов`;
            
        } catch (error) {
            console.error("Ошибка при обработке данных:", error);
        }
    });
}

function updateFileList(listId, files, folderType) {
    var listElem = document.getElementById(listId);
    listElem.innerHTML = "";
    
    if (!files || files.length === 0) {
        var li = document.createElement("li");
        li.className = "empty-message";
        li.textContent = "Нет файлов.";
        listElem.appendChild(li);
        return;
    }
    
    
    
    files.forEach(function(file) {
        var li = document.createElement("li");
        li.className = "file-item";
        
        
        let fileName, filePath;
        if (typeof file === 'object' && file.name) {
            fileName = file.name;
            filePath = file.path;
        } else {
            
            filePath = file;
            fileName = file.split('\\').pop().split('/').pop();
        }
        
        li.textContent = fileName;
        li.dataset.fullpath = filePath;
        li.dataset.file = fileName;
        li.dataset.folderType = folderType;
        li.draggable = true;
        
        
        const extension = ('.' + fileName.split('.').pop()).toLowerCase();
        if (['.mp3', '.wav', '.ogg', '.flac', '.aif', '.aiff', '.m4a', '.wma'].includes(extension)) {
            li.classList.add('audio');
        } else if (['.mp4', '.avi', '.mov', '.mkv', '.wmv'].includes(extension)) {
            li.classList.add('video');
        } else if (['.txt', '.srt', '.ass', '.ssa', '.vtt'].includes(extension)) {
            li.classList.add('text');
        }
        
        li.addEventListener('dragstart', dragStart);
        li.addEventListener('click', function() {
            
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
            li.classList.add('selected');
            
            
            pyBridge.openFile(filePath);
        });
        
        listElem.appendChild(li);
    });
}

function openFolderForType(folderType) {
    if (!currentSeason || !selectedEpisodeLi) {
        alert("Выберите сезон и эпизод.");
        return;
    }
    pyBridge.openFolderForType(currentProject, currentSeason, currentEpisode, folderType, function(response) {
    });
}


function allowDrop(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
}

function dragStart(event) {
    var fullpath = event.target.dataset.fullpath;
    if (fullpath) {
        event.dataTransfer.setData("text/uri-list", "file:
        event.dataTransfer.setData("text/plain", fullpath);
        event.dataTransfer.setData("folderType", event.target.dataset.folderType);
        event.dataTransfer.setData("source-type", event.target.dataset.folderType);

        event.target.classList.add('dragged');
        
        
        window.currentDraggedElement = event.target;

        event.dataTransfer.effectAllowed = "copyMove";
    }
}


function dragEnterUI() {
    
    document.body.classList.add('dragging');
    
    
    document.querySelectorAll('.file-list').forEach(list => {
        list.classList.add('potential-drop-target');
    });
}


function dragLeaveUI() {
    
    document.body.classList.remove('dragging');
    
    
    document.querySelectorAll('.potential-drop-target').forEach(list => {
        list.classList.remove('potential-drop-target');
    });
    
    
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
    
    
    window.currentDropTarget = null;
}


function dragEnd() {
    document.body.classList.remove('dragging');
    
    
    document.querySelectorAll('.potential-drop-target').forEach(list => {
        list.classList.remove('potential-drop-target');
    });
    
    
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


function drop(event, targetType) {
    event.preventDefault();
    event.stopPropagation();
    
    
    document.querySelectorAll('.drop-target').forEach(el => {
        el.classList.remove('drop-target');
    });
    
    
    document.querySelectorAll('.drop-target-container').forEach(el => {
        el.classList.remove('drop-target-container');
        el.removeAttribute('data-highlight-type');
    });
    
    
    document.querySelectorAll('.potential-drop-target').forEach(list => {
        list.classList.remove('potential-drop-target');
    });
    
    
    dragEnd();
    
    
    const filePath = event.dataTransfer.getData('text/plain');
    const sourceType = event.dataTransfer.getData('source-type') || event.dataTransfer.getData('folderType');
    
    
    if (filePath) {
        
        if (sourceType !== targetType) {
            
            
            if (currentProject && currentSeason && currentEpisode) {
                
                pyBridge.moveFile(filePath, targetType, currentProject, currentSeason, currentEpisode, function(result) {
                    if (result === "success") {
                        
                        updateRightPanel(currentSeason, currentEpisode);
                        showToast(`Файл перемещен в ${getTypeName(targetType)}`, 'success');
                    } else {
                        showToast('Не удалось переместить файл', 'error');
                        console.error('Ошибка при перемещении файла:', result);
                    }
                });
            } else {
                alert('Выберите проект, сезон и эпизод');
            }
        } else {
            
        }
    } else {
        
        
    }
}


function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, duration);
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


function initDragDropHandlers() {
    
    
    document.addEventListener('dragstart', function(event) {
        
        if (event.target.classList.contains('file-item')) {
            dragEnterUI();
        }
    });
    
    document.addEventListener('dragend', function() {
        dragLeaveUI();
    });
    
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            dragEnd();
        }
    });
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


function handleClearList(listId) {
    const list = document.getElementById(listId);
    if (list) {
        
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
        
        
        updateFileCounter(listId);
    }
}


document.addEventListener('DOMContentLoaded', function() {
    initDragDropHandlers();
});
