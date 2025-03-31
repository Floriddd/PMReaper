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
            
            // Создаем контейнер для названия директории
            var dirNameSpan = document.createElement("span");
            dirNameSpan.className = "dir-name";
            dirNameSpan.textContent = dirName;
            dirNameSpan.title = dir;
            li.appendChild(dirNameSpan);
            
            // Создаем контейнер для кнопок
            var controlsDiv = document.createElement("div");
            controlsDiv.className = "dir-controls";
            
            // Кнопка выбора директории
            var selectBtn = document.createElement("button");
            selectBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
            selectBtn.className = "dir-open-btn";
            selectBtn.title = "Выбрать директорию";
            selectBtn.onclick = function() { setCurrentBaseDir(index); };
            controlsDiv.appendChild(selectBtn);
            
            // Кнопка удаления директории
            var deleteBtn = document.createElement("button");
            deleteBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/></svg>';
            deleteBtn.className = "dir-delete-btn";
            deleteBtn.title = "Удалить директорию";
            deleteBtn.onclick = function() {
                if (confirm("Удалить директорию " + dir + "?")) {
                    deleteBaseDir(index);
                }
            };
            controlsDiv.appendChild(deleteBtn);
            
            li.appendChild(controlsDiv);
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
            
            var projectNameSpan = document.createElement("span");
            projectNameSpan.className = "project-name";
            projectNameSpan.textContent = proj;
            li.appendChild(projectNameSpan);
            
            var controlsDiv = document.createElement("div");
            controlsDiv.className = "project-controls";

            var editBtn = document.createElement("button");
            editBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>';
            editBtn.className = "project-edit-btn";
            editBtn.title = "Редактировать проект";
            editBtn.onclick = function() { toggleProjectEdit(li, proj); };
            controlsDiv.appendChild(editBtn);

            var openBtn = document.createElement("button");
            openBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>';
            openBtn.className = "project-open-btn";
            openBtn.title = "Открыть проект";
            openBtn.onclick = function() { openProject(proj); };
            controlsDiv.appendChild(openBtn);

            var deleteBtn = document.createElement("button");
            deleteBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/></svg>';
            deleteBtn.className = "project-delete-btn";
            deleteBtn.title = "Удалить проект";
            deleteBtn.onclick = function() {
                if (confirm("Удалить проект " + proj + "?")) {
                    deleteProject(proj);
                }
            };
            controlsDiv.appendChild(deleteBtn);

            li.appendChild(controlsDiv);
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

            var headerContainer = document.createElement("div");
            headerContainer.className = "season-header";
            
            var header = document.createElement("h3");
            header.textContent = season + " сезон";
            headerContainer.appendChild(header);

            var buttonsContainer = document.createElement("div");
            buttonsContainer.className = "season-controls";

            var editSeasonBtn = document.createElement("button");
            editSeasonBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>';
            editSeasonBtn.className = "season-edit-btn";
            editSeasonBtn.title = "Редактировать сезон";
            editSeasonBtn.onclick = function() { toggleSeasonEdit(season, seasonDiv); };
            buttonsContainer.appendChild(editSeasonBtn);

            var openSeasonBtn = document.createElement("button");
            openSeasonBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>';
            openSeasonBtn.className = "season-open-btn";
            openSeasonBtn.title = "Открыть папку сезона";
            openSeasonBtn.onclick = function() { openSeasonFolder(season); };
            buttonsContainer.appendChild(openSeasonBtn);

            var deleteSeasonBtn = document.createElement("button");
            deleteSeasonBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/></svg>';
            deleteSeasonBtn.className = "season-delete-btn";
            deleteSeasonBtn.title = "Удалить сезон";
            deleteSeasonBtn.onclick = function() {
                if (confirm("Удалить сезон " + season + " и все его эпизоды?")) {
                    deleteSeason(season);
                }
            };
            buttonsContainer.appendChild(deleteSeasonBtn);
            
            headerContainer.appendChild(buttonsContainer);
            seasonDiv.appendChild(headerContainer);

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
                    editEpBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>';
                    editEpBtn.className = "episode-edit-btn";
                    editEpBtn.title = "Редактировать эпизод";
                    editEpBtn.onclick = function() { toggleEpisodeEdit(season, ep, li); };
                    li.appendChild(editEpBtn);

                    var openEpBtn = document.createElement("button");
                    openEpBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path></svg>';
                    openEpBtn.className = "episode-open-btn";
                    openEpBtn.title = "Открыть папку эпизода";
                    openEpBtn.onclick = function() { openEpisodeFolder(season, ep); };
                    li.appendChild(openEpBtn);

                    var openRppBtn = document.createElement("button");
                    openRppBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 3l14 9-14 9V3z"></path></svg>';
                    openRppBtn.className = "episode-launch-btn";
                    openRppBtn.title = "Запустить проект";
                    openRppBtn.onclick = function() { openProjectFile(season, ep); };
                    li.appendChild(openRppBtn);

                    var deleteEpBtn = document.createElement("button");
                    deleteEpBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2M10 11v6M14 11v6"/></svg>';
                    deleteEpBtn.className = "episode-delete-btn";
                    deleteEpBtn.title = "Удалить эпизод";
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
            addEpBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg> Добавить серию';
            addEpBtn.className = "add-episode-btn";
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
        saveBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg> Сохранить';
        saveBtn.className = "season-save-btn";
        saveBtn.title = "Сохранить";
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
        var saveBtn = seasonDiv.querySelector("button.season-save-btn");
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
        saveBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 01-2-2V5a2 2 0 012-2h11l5 5v11a2 2 0 01-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg> Сохранить';
        saveBtn.className = "episode-save-btn";
        saveBtn.title = "Сохранить";
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
        var saveBtn = li.querySelector("button.episode-save-btn");
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

function toggleProjectEdit(li, projectName) {
    // Находим существующий элемент названия проекта или форму редактирования
    var input = li.querySelector("input.projectEditInput");
    
    if (!input) {
        // Режим редактирования
        var nameSpan = li.querySelector(".project-name");
        if (!nameSpan) {
            console.error("Не найден элемент с классом .project-name");
            return;
        }
        
        var oldProjectName = nameSpan.textContent;
        
        // Сохраняем оригинальное содержимое
        var originalContent = nameSpan.innerHTML;
        
        // Скрываем название проекта
        nameSpan.style.display = "none";
        
        // Создаем поле ввода
        input = document.createElement("input");
        input.type = "text";
        input.className = "projectEditInput";
        input.value = oldProjectName;
        li.insertBefore(input, nameSpan);
        
        // Создаем кнопку сохранения
        var saveBtn = document.createElement("button");
        saveBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M13.5 8.5L5.5 13.5L5.5 3.5L13.5 8.5Z" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>';
        saveBtn.className = "project-save-btn";
        saveBtn.title = "Сохранить";
        
        // Обработчик для кнопки сохранения
        saveBtn.onclick = function() {
            var newProjectName = input.value.trim();
            
            if (newProjectName === '' || newProjectName === oldProjectName) {
                // Если имя не изменилось или пустое, восстанавливаем исходное состояние
                nameSpan.style.display = "";
                saveBtn.remove();
                input.remove();
                return;
            }
            
            console.log(`Переименование проекта: ${oldProjectName} -> ${newProjectName}`);
            
            try {
                // Вызываем метод переименования проекта
                var result = pyBridge.renameProjectFolder(oldProjectName, newProjectName);
                
                // Проверяем, является ли результат Promise
                if (result && typeof result.then === 'function') {
                    result.then(function(response) {
                        console.log("Ответ после переименования:", response);
                        
                        if (response === "success") {
                            showToast("Проект переименован", "success");
                            refreshProjectList();
                        } else {
                            // Если ответ начинается с "error:", отображаем ошибку
                            if (response && response.startsWith("error:")) {
                                showToast("Ошибка при переименовании: " + response.substring(6), "error");
                            } else {
                                showToast("Ошибка при переименовании: " + response, "error");
                            }
                            
                            // Восстанавливаем исходное состояние
                            nameSpan.style.display = "";
                            saveBtn.remove();
                            input.remove();
                        }
                    }).catch(function(error) {
                        console.error("Ошибка при переименовании:", error);
                        showToast("Ошибка при переименовании: " + error, "error");
                        
                        // Восстанавливаем исходное состояние
                        nameSpan.style.display = "";
                        saveBtn.remove();
                        input.remove();
                    });
                } else {
                    // Если результат не Promise, обрабатываем как синхронный ответ
                    console.log("Синхронный ответ после переименования:", result);
                    
                    if (result === "success") {
                        showToast("Проект переименован", "success");
                        refreshProjectList();
                    } else {
                        // Если ответ начинается с "error:", отображаем ошибку
                        if (result && result.startsWith("error:")) {
                            showToast("Ошибка при переименовании: " + result.substring(6), "error");
                        } else {
                            showToast("Ошибка при переименовании: " + result, "error");
                        }
                        
                        // Восстанавливаем исходное состояние
                        nameSpan.style.display = "";
                        saveBtn.remove();
                        input.remove();
                    }
                }
            } catch (e) {
                console.error("Ошибка при вызове метода переименования:", e);
                showToast("Ошибка при вызове метода переименования", "error");
                
                // Восстанавливаем исходное состояние
                nameSpan.style.display = "";
                saveBtn.remove();
                input.remove();
            }
        };
        
        // Добавляем кнопку сохранения перед контролами
        var controlsDiv = li.querySelector('.project-controls');
        if (controlsDiv) {
            li.insertBefore(saveBtn, controlsDiv);
        } else {
            li.appendChild(saveBtn);
        }
        
        // Устанавливаем фокус на поле ввода
        input.focus();
    } else {
        // Режим отмены редактирования
        var nameSpan = li.querySelector(".project-name");
        if (nameSpan) {
            nameSpan.style.display = "";
        }
        
        var saveBtn = li.querySelector(".project-save-btn");
        if (saveBtn) saveBtn.remove();
        
        input.remove();
    }
}