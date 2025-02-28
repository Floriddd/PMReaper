// Файл file-manager.js - работа с файлами и drag-n-drop

var selectedEpisodeLi = null;

function selectEpisode(season, episode, liElement) {
    if (selectedEpisodeLi && selectedEpisodeLi !== liElement) {
        selectedEpisodeLi.classList.remove('selected');
    }
    liElement.classList.add('selected');
    selectedEpisodeLi = liElement;

    currentSeason = season;
    currentEpisode = episode;
    console.log("JS: selectEpisode - currentSeason set to:", currentSeason, ", currentEpisode:", currentEpisode);
    pyBridge.setCurrentSeasonEpisode(season, episode);

    updateRightPanel(season, episode);
}

function updateRightPanel(season, episode) {
    pyBridge.listFolderContent(currentProject, season, episode, function(response) {
        var content = JSON.parse(response);
        console.log("Обновление файлов:", content);
        updateFileList("rawsList", content.raws, 'raws');
        updateFileList("roadsList", content.roads, 'roads');
        updateFileList("voiceList", content.voice, 'voice');
        updateFileList("subsList", content.subs, 'subs');
    });
}

function updateFileList(listId, files, folderType) {
    var listElem = document.getElementById(listId);
    listElem.innerHTML = "";
    if (files && files.length > 0) {
        files.sort((a, b) => a.name.localeCompare(b.name));
        files.forEach(function(fileObj) {
            var li = document.createElement("li");
            li.className = "file-item";
            li.textContent = fileObj.name;
            li.draggable = true;
            li.dataset.file = fileObj.name;
            li.dataset.folderType = folderType;
            li.dataset.fullpath = fileObj.path;
            li.addEventListener('dragstart', dragStart);
            listElem.appendChild(li);
        });
    } else {
        var li = document.createElement("li");
        li.textContent = "Нет файлов.";
        listElem.appendChild(li);
    }
}

function openFolderForType(folderType) {
    if (!currentSeason || !selectedEpisodeLi) {
        alert("Выберите сезон и эпизод.");
        return;
    }
    pyBridge.openFolderForType(currentProject, currentSeason, currentEpisode, folderType, function(response) {
        console.log(response);
    });
}

// Функции для drag-n-drop
function allowDrop(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = "copy";
    console.log("allowDrop triggered");
}

function dragStart(event) {
    var fullpath = event.target.dataset.fullpath;
    if (fullpath) {
        event.dataTransfer.setData("text/uri-list", "file:///" + fullpath.replace(/\\/g, '/'));
        event.dataTransfer.setData("text/plain", fullpath);
        event.dataTransfer.setData("folderType", event.target.dataset.folderType);

        event.target.classList.add('dragged');

        event.dataTransfer.effectAllowed = "copyMove";
    }
}

function dragEnter(event) {
    event.preventDefault();
    event.stopPropagation();
    console.log("dragEnter triggered");
    document.body.classList.add('drop-target-container');
}

function dragLeave(event) {
    event.preventDefault();
    event.stopPropagation();
    console.log("dragLeave triggered");
    setTimeout(() => {
        document.body.classList.remove('drop-target-container');
    }, 100);
}

function dragEnd() {
    document.body.classList.remove('drop-target-container');
}

function drop(event) {
    event.preventDefault();
    console.log("drop event triggered");
    dragEnd();
}

// Инициализация обработчиков перетаскивания
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('dragenter', dragEnter);
    document.addEventListener('dragover', allowDrop);
    document.addEventListener('dragleave', dragLeave);
    document.addEventListener('drop', drop);
    document.addEventListener('dragend', dragEnd);
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            dragEnd();
        }
    });
});