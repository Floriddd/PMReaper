var pyBridge;
var currentProject = "";
var currentSeason = "";
var currentBaseDir = "";
var currentEpisode = "";
var episodesData = {};

new QWebChannel(qt.webChannelTransport, function(channel) {
    pyBridge = channel.objects.pyBridge;
    refreshBaseDirList();
    refreshProjectList();
});

function setBaseDir() {
    var path = document.getElementById("baseDir").value;
    pyBridge.setBaseDirectory(path, function(response) {
        console.log(response);
    });
}

function browseBaseDir() {
    pyBridge.browseDirectory(function(path) {
        if (path) {
            document.getElementById("newBaseDir").value = path;
            console.log("Папка выбрана: " + path);
        }
    });
}

function refreshBaseDirList() {
    pyBridge.listBaseDirectories(function(response) {
        var baseDirs = JSON.parse(response);
        var listElem = document.getElementById("baseDirList");
        listElem.innerHTML = "";
        baseDirs.forEach(function(dir, index) {
            var li = document.createElement("li");
            var dirName = dir;
            if (dir.length > 50) {
                dirName = "..." + dir.slice(-50);
            }
            li.textContent = dirName;
            li.title = dir;

            var selectBtn = document.createElement("button");
            selectBtn.textContent = "➡️";
            selectBtn.onclick = function() { setCurrentBaseDir(index); };
            li.appendChild(selectBtn);

            var deleteBtn = document.createElement("button");
            deleteBtn.textContent = "❌";
            deleteBtn.onclick = function() {
                if (confirm("Удалить директорию " + dir + "?")) {
                    deleteBaseDir(index);
                }
            };
            li.appendChild(deleteBtn);

            listElem.appendChild(li);
        });
    });
}

function addBaseDir() {
    var path = document.getElementById("newBaseDir").value;
    if (!path) return;
    pyBridge.addBaseDirectory(path, function(response) {
        console.log(response);
        refreshBaseDirList();
        document.getElementById("newBaseDir").value = "";
    });
}

function deleteBaseDir(index) {
    pyBridge.deleteBaseDirectory(index, function(response) {
        console.log(response);
        refreshBaseDirList();
        refreshProjectList();
    });
}
function setCurrentBaseDir(index) {
    pyBridge.setCurrentBaseDirectory(index, function(response) {
        console.log(response);
        refreshProjectList();
        showSection('projectListSection');
        document.getElementById("currentBaseDirName").textContent = currentBaseDir;
});
}

function refreshProjectList() {
    pyBridge.listProjects(function(response) {
        console.log("JS: Ответ от listProjects:", response);
        var projects = JSON.parse(response);
        if (projects === null) {
            projects = [];
        }
        var listElem = document.getElementById("projectList");
        listElem.innerHTML = "";
        projects.forEach(function(proj) {
            var li = document.createElement("li");
            li.textContent = proj + " ";

            var openBtn = document.createElement("button");
            openBtn.textContent = "➡️";
            openBtn.onclick = function() { openProject(proj); };
            li.appendChild(openBtn);

            var deleteBtn = document.createElement("button");
            deleteBtn.textContent = "❌";
            deleteBtn.onclick = function() {
                if (confirm("Удалить проект " + proj + "?")) {
                    deleteProject(proj);
                }
            };
            li.appendChild(deleteBtn);

            listElem.appendChild(li);
        });
    });
}

function createProject() {
    var projectName = document.getElementById("newProjectName").value.trim();
    if (!projectName) return;
    pyBridge.createProject(projectName, function(response) {
        console.log(response);
        refreshProjectList();
    });
}

function deleteProject(projectName) {
    pyBridge.deleteProject(projectName, function(response) {
        console.log(response);
        refreshProjectList();
    });
}

function openProject(projectName) {
    currentProject = projectName;
    currentSeason = "";
    currentEpisode = "";
    console.log("JS: openProject - currentProject set to:", currentProject);
    pyBridge.setCurrentProject(projectName);

    document.getElementById("currentProjectName").textContent = projectName;
    showSection("projectDetailSection");
    refreshTree();
}


function backToProjects() {
    showSection("projectListSection");
}

function backToBaseDirList() {
    showSection("baseDirSection");
}

function refreshTree() {

    pyBridge.listEpisodes(currentProject, function(response) {
        episodesData = JSON.parse(response);
        var container = document.getElementById("treeContainer");
        container.innerHTML = "";
        var seasons = Object.keys(episodesData).map(Number).sort(function(a, b){return a-b});

        seasons.forEach(function(season) {
            var seasonDiv = document.createElement("div");
            seasonDiv.className = "season";
            seasonDiv.dataset.season = season;

            var header = document.createElement("h3");
            header.textContent = season + " сезон";
            seasonDiv.appendChild(header);

            var editSeasonBtn = document.createElement("button");
            editSeasonBtn.textContent = "✏️";
            editSeasonBtn.onclick = function() { toggleSeasonEdit(season, seasonDiv); };
            seasonDiv.appendChild(editSeasonBtn);

            var openSeasonBtn = document.createElement("button");
            openSeasonBtn.textContent = "📂";
            openSeasonBtn.onclick = function() { openSeasonFolder(season); };
            seasonDiv.appendChild(openSeasonBtn);

            var deleteSeasonBtn = document.createElement("button");
            deleteSeasonBtn.textContent = "❌";
            deleteSeasonBtn.onclick = function() {
                if (confirm("Удалить сезон " + season + " и все его эпизоды?")) {
                    deleteSeason(season);
                }
            };
            seasonDiv.appendChild(deleteSeasonBtn);

            var epList = document.createElement("ul");
            if (episodesData[season] && episodesData[season].length > 0) {
                episodesData[season].sort(function(a, b){return a-b});
                episodesData[season].forEach(function(ep) {
                    var li = document.createElement("li");
                    li.dataset.episode = ep;
                    li.dataset.season = season;
                    li.className = "episode";
                    li.textContent = ep + " серия ";
                    li.addEventListener('click', function() {
                        selectEpisode(season, ep, li);
                    });

                    var editEpBtn = document.createElement("button");
                    editEpBtn.textContent = "✏️";
                    editEpBtn.onclick = function() { toggleEpisodeEdit(season, ep, li); };
                    li.appendChild(editEpBtn);

                    var openEpBtn = document.createElement("button");
                    openEpBtn.textContent = "📂";
                    openEpBtn.onclick = function() { openEpisodeFolder(season, ep); };
                    li.appendChild(openEpBtn);

                    var openRppBtn = document.createElement("button");
                    openRppBtn.textContent = "Запустить";
                    openRppBtn.onclick = function() { openProjectFile(season, ep); };
                    li.appendChild(openRppBtn);

                    var deleteEpBtn = document.createElement("button");
                    deleteEpBtn.textContent = "❌";
                    deleteEpBtn.onclick = function() {
                        if (confirm("Удалить эпизод " + ep + " сезона " + season + "?")) {
                            deleteEpisode(season, ep);
                        }
                    };
                    li.appendChild(deleteEpBtn);

                    epList.appendChild(li);
                });
            } else {
                var p = document.createElement("p");
                p.textContent = "Нет эпизодов.";
                seasonDiv.appendChild(p);
            }
            var addEpBtn = document.createElement("button");
            addEpBtn.textContent = "+ Добавить серию";
            addEpBtn.onclick = function() { addEpisode(season); };

            seasonDiv.appendChild(epList);
            seasonDiv.appendChild(addEpBtn);

            container.appendChild(seasonDiv);
        });
        if (seasons.length === 0) {
            container.innerHTML = "<p>Нет сезонов. Добавьте сезон.</p>";
        }
    });

}

function addSeason() {
    var seasons = Object.keys(episodesData).map(Number);
    var nextSeason = seasons.length > 0 ? Math.max(...seasons) + 1 : 1;
    pyBridge.addSeason(currentProject, nextSeason, function(response) {
        console.log(response);
        refreshTree();
    });
}

function addEpisode(season) {
    var eps = episodesData[season] || [];
    var nextEpisode = eps.length > 0 ? Math.max(...eps) + 1 : 1;
    pyBridge.addEpisode(currentProject, season, nextEpisode, function(response) {
        console.log(response);
        refreshTree();
    });
}

function deleteEpisode(season, episode) {
    pyBridge.deleteEpisode(currentProject, season, episode, function(response) {
        console.log(response);
        refreshTree();
    });
}

function deleteSeason(season) {
    pyBridge.deleteSeason(currentProject, season, function(response) {
        console.log(response);
        refreshTree();
    });
}

function openEpisodeFolder(season, episode) {
    pyBridge.openEpisodeFolder(currentProject, season, episode, function(response) {
        currentSeason = season;
        console.log(response);
    });
}

function openSeasonFolder(season) {
    pyBridge.openSeasonFolder(currentProject, season, function(response) {
        console.log(response);
    });
}

function openProjectFile(season, episode) {
    pyBridge.openProjectFile(currentProject, season, episode, function(response) {
        console.log(response);
    });
}

function toggleSeasonEdit(oldSeason, seasonDiv) {
    var input = seasonDiv.querySelector("input.seasonEditInput");
    if (!input) {
        input = document.createElement("input");
        input.type = "number";
        input.className = "seasonEditInput";
        input.value = oldSeason;
        seasonDiv.appendChild(input);
        var saveBtn = document.createElement("button");
        saveBtn.textContent = "Сохранить";
        saveBtn.className = "seasonSaveBtn";
        saveBtn.onclick = function() {
            var newSeason = parseInt(input.value);
            if (isNaN(newSeason) || newSeason <= 0) {
                console.log("Неверный номер сезона");
                return;
            }
            pyBridge.renameSeason(currentProject, oldSeason, newSeason, function(response) {
                console.log(response);
                refreshTree();
            });
        };
        seasonDiv.appendChild(saveBtn);
    } else {
        var saveBtn = seasonDiv.querySelector("button.seasonSaveBtn");
        if (saveBtn) saveBtn.remove();
        input.remove();
    }
}

function toggleEpisodeEdit(season, oldEpisode, li) {
    var input = li.querySelector("input.episodeEditInput");
    if (!input) {
        input = document.createElement("input");
        input.type = "number";
        input.className = "episodeEditInput";
        input.value = oldEpisode;
        li.appendChild(input);
        var saveBtn = document.createElement("button");
        saveBtn.textContent = "Сохранить";
        saveBtn.className = "episodeSaveBtn";
        saveBtn.onclick = function() {
            var newEpisode = parseInt(input.value);
            if (isNaN(newEpisode) || newEpisode <= 0) {
                console.log("Неверный номер эпизода");
                return;
            }
            pyBridge.renameEpisode(currentProject, season, oldEpisode, newEpisode, function(response) {
            console.log(response);
            refreshTree();
            });
        };
        li.appendChild(saveBtn);
    } else {
        var saveBtn = li.querySelector("button.episodeSaveBtn");
        if (saveBtn) saveBtn.remove();
        input.remove();
    }
}

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
    if (!season || !episode || !currentProject) {
        return;
    }
    
    console.log(`Запрос файлов для проекта: ${currentProject}, сезон: ${season}, эпизод: ${episode}`);
    
    // Используем новую функцию getFilesByType из моста
    pyBridge.getFilesByType(currentProject, season, episode, function(filesByType) {
        console.log("Получены файлы:", filesByType);
        
        try {
            // Парсим JSON, если это строка
            const files = typeof filesByType === 'string' ? JSON.parse(filesByType) : filesByType;
            
            // Обновляем списки файлов
            updateFileList('rawsList', files.raws || [], 'raws');
            updateFileList('roadsList', files.roads || [], 'roads');
            updateFileList('voiceList', files.voice || [], 'voice');
            updateFileList('subsList', files.subs || [], 'subs');
            
            // Обновляем счетчики файлов
            const rawsCounter = document.getElementById('rawsCounter');
            if (rawsCounter) rawsCounter.textContent = `${files.raws ? files.raws.length : 0} файлов`;
            
            const roadsCounter = document.getElementById('roadsCounter');
            if (roadsCounter) roadsCounter.textContent = `${files.roads ? files.roads.length : 0} файлов`;
            
            const voiceCounter = document.getElementById('voiceCounter');
            if (voiceCounter) voiceCounter.textContent = `${files.voice ? files.voice.length : 0} файлов`;
            
            const subsCounter = document.getElementById('subsCounter');
            if (subsCounter) subsCounter.textContent = `${files.subs ? files.subs.length : 0} файлов`;
            
            console.log("Панель обновлена успешно");
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
    
    // Для совместимости со старым форматом (когда файлы были объектами с name и path)
    // и новым форматом (когда файлы - это просто пути)
    files.forEach(function(file) {
        var li = document.createElement("li");
        li.className = "file-item";
        
        // Проверяем, является ли файл объектом или строкой (путь)
        let fileName, filePath;
        if (typeof file === 'object' && file.name) {
            fileName = file.name;
            filePath = file.path;
        } else {
            // Получаем имя файла из пути
            filePath = file;
            fileName = file.split('\\').pop().split('/').pop();
        }
        
        li.textContent = fileName;
        li.dataset.fullpath = filePath;
        li.dataset.file = fileName;
        li.dataset.folderType = folderType;
        li.draggable = true;
        
        // Определяем тип файла по расширению для стилизации
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
            // Выделяем файл
            document.querySelectorAll('.file-item').forEach(el => el.classList.remove('selected'));
            li.classList.add('selected');
            
            // Открываем файл
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
        console.log(response);
    });
}

function showSection(sectionId) {
    document.getElementById("projectListSection").classList.add("hidden");
    document.getElementById("projectDetailSection").classList.add("hidden");
    document.getElementById("selectProjectDirSection").classList.add("hidden");
    document.getElementById(sectionId).classList.remove("hidden");
}

function allowDrop(event) {
    event.preventDefault();
}

function dragStart(event) {
    var fullpath = event.target.dataset.fullpath;
    if (fullpath) {
        event.dataTransfer.setData("text/uri-list", "file:///" + fullpath.replace(/\\/g, '/'));
        event.dataTransfer.setData("text/plain", fullpath);
        event.dataTransfer.setData("folderType", event.target.dataset.folderType);
        event.dataTransfer.setData("source-type", event.target.dataset.folderType);

        event.target.classList.add('dragged');

        // Сохраняем source element для обновления UI
        window.currentDraggedElement = event.target;
        
        event.dataTransfer.effectAllowed = "copyMove";
    }
}


function drop(event, targetFolderType) {
    event.preventDefault();
    event.stopPropagation();
    console.log("Drop на папку:", targetFolderType);
    
    // Убираем классы drop-target
    document.querySelectorAll('.drop-target').forEach(el => {
        el.classList.remove('drop-target');
    });
    
    // Убираем подсветку родительских контейнеров
    document.querySelectorAll('.drop-target-container').forEach(el => {
        el.classList.remove('drop-target-container');
        el.removeAttribute('data-highlight-type');
    });
    
    // Получаем исходный путь и тип папки
    const filePath = event.dataTransfer.getData('text/plain');
    const sourceType = event.dataTransfer.getData('source-type') || event.dataTransfer.getData('folderType');
    
    // Если filePath существует - это внутреннее перетаскивание
    if (filePath) {
        // Проверяем, что источник и цель разные
        if (sourceType !== targetFolderType) {
            console.log(`Перемещение файла из ${sourceType} в ${targetFolderType}: ${filePath}`);
            
            // Проверяем, что все необходимые данные есть
            if (currentProject && currentSeason && currentEpisode) {
                // Вызываем функцию мостика для перемещения файла
                pyBridge.moveFile(filePath, targetFolderType, currentProject, currentSeason, currentEpisode, function(result) {
                    if (result === "success") {
                        // Обновляем панель
                        updateRightPanel(currentSeason, currentEpisode);
                        showToast(`Файл перемещен в ${getTypeName(targetFolderType)}`, 'success');
                    } else {
                        showToast('Не удалось переместить файл', 'error');
                        console.error('Ошибка при перемещении файла:', result);
                    }
                });
            } else {
                showToast('Выберите проект, сезон и эпизод', 'warning');
            }
        } else {
            // Если тип тот же самый, ничего не делаем
            console.log('Перетаскивание в ту же папку, игнорируем');
        }
    } else {
        // Внешнее перетаскивание (из файлового менеджера)
        // Данный функционал обрабатывается PyQt, не в JavaScript
        console.log('Внешнее перетаскивание, ожидается обработка в PyQt');
    }
}

/**
 * Показывает toast-уведомление
 * @param {string} message - Сообщение для отображения
 * @param {string} type - Тип уведомления (success, error, warning)
 */
function showToast(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Показываем toast
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Скрываем через указанное время
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, duration);
}

/**
 * Возвращает отображаемое имя типа папки
 * @param {string} type - Тип папки
 * @returns {string} - Отображаемое имя
 */
function getTypeName(type) {
    const typeNames = {
        'raws': 'Равки',
        'roads': 'Делённые дороги',
        'voice': 'Озвучка',
        'subs': 'Субтитры'
    };
    
    return typeNames[type] || type;
}