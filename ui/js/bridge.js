// Файл bridge.js - взаимодействие с Python через QWebChannel

var pyBridge;

// Инициализация моста между JS и Python
new QWebChannel(qt.webChannelTransport, function(channel) {
    pyBridge = channel.objects.pyBridge;
    refreshBaseDirList();
    refreshProjectList();
});

// Функции для работы с базовыми директориями
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