var pyBridge;
var currentProject = "";
var currentSeason = "";
var currentBaseDir = "";
var currentEpisode = "";
var episodesData = {};
var draggedFileInfo = null;
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
        refreshProjectList(); // Обновить список проектов после удаления базовой директории
    });
}
function setCurrentBaseDir(index) {
    pyBridge.setCurrentBaseDirectory(index, function(response) {
        console.log(response);
        refreshProjectList(); // Обновить список проектов для новой базовой директории
        showSection('projectListSection');
        document.getElementById("currentBaseDirName").textContent = currentBaseDir;
});
}

function refreshProjectList() {
    pyBridge.listProjects(function(response) {
        console.log("JS: Ответ от listProjects:", response); // <--- Добавлено для отладки
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
pyBridge.listFolderContent(currentProject, season, episode, function(response) {
var content = JSON.parse(response);
console.log("Folder content:", content);
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
    files.sort();
files.forEach(function(file) {
var li = document.createElement("li");
li.className = "file-item";
li.textContent = file;
li.draggable = true;
li.dataset.file = file;
li.dataset.folderType = folderType;
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
    draggedFileInfo = {
        file: event.target.dataset.file,
        sourceFolderType: event.target.dataset.folderType
    };
    event.dataTransfer.setData("text/plain", JSON.stringify(draggedFileInfo));
}


function drop(event, targetFolderType) {
    event.preventDefault();
}