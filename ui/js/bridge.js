

var pyBridge;


new QWebChannel(qt.webChannelTransport, function(channel) {
    pyBridge = channel.objects.pyBridge;
    refreshBaseDirList();
    refreshProjectList();
});


function browseBaseDir() {
    pyBridge.browseDirectory(function(path) {
        if (path) {
            document.getElementById("newBaseDir").value = path;
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
        refreshBaseDirList();
        document.getElementById("newBaseDir").value = "";
    });
}

function deleteBaseDir(index) {
    pyBridge.deleteBaseDirectory(index, function(response) {
        refreshBaseDirList();
        refreshProjectList();
    });
}

function setCurrentBaseDir(index) {
    pyBridge.setCurrentBaseDirectory(index, function(response) {
        refreshProjectList();
        showSection('projectListSection');
        document.getElementById("currentBaseDirName").textContent = currentBaseDir;
    });
}


function convertProjectStructure(projectName) {
    if (confirm("Конвертировать структуру проекта " + projectName + " в новый формат? Это может занять некоторое время. ВАЖНО! конвертирует только со старой структуры программы")) {
        pyBridge.convertProjectStructure(projectName, function(response) {
            alert(response);
            refreshProjectList(); 
        });
    }
}
