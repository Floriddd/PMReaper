// Файл ui-utils.js - вспомогательные функции для пользовательского интерфейса

function showSection(sectionId) {
    document.getElementById("projectListSection").classList.add("hidden");
    document.getElementById("projectDetailSection").classList.add("hidden");
    document.getElementById("selectProjectDirSection").classList.add("hidden");
    document.getElementById(sectionId).classList.remove("hidden");
}