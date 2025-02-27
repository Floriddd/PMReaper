// Файл projects.js - работа с проектами

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