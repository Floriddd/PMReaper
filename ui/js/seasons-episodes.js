

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
        refreshTree();
    });
}

function addEpisode(season) {
    var eps = episodesData[season] || [];
    var nextEpisode = eps.length > 0 ? Math.max(...eps) + 1 : 1;
    pyBridge.addEpisode(currentProject, season, nextEpisode, function(response) {
        refreshTree();
    });
}

function deleteEpisode(season, episode) {
    pyBridge.deleteEpisode(currentProject, season, episode, function(response) {
        refreshTree();
    });
}

function deleteSeason(season) {
    pyBridge.deleteSeason(currentProject, season, function(response) {
        refreshTree();
    });
}

function openEpisodeFolder(season, episode) {
    pyBridge.openEpisodeFolder(currentProject, season, episode, function(response) {
        currentSeason = season;
    });
}

function openSeasonFolder(season) {
    pyBridge.openSeasonFolder(currentProject, season, function(response) {
    });
}

function openProjectFile(season, episode) {
    pyBridge.openProjectFile(currentProject, season, episode, function(response) {
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
                return;
            }
            pyBridge.renameSeason(currentProject, oldSeason, newSeason, function(response) {
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
                return;
            }
            pyBridge.renameEpisode(currentProject, season, oldEpisode, newEpisode, function(response) {
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
