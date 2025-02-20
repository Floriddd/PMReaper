import os
import sys
import json
import shutil
import appdirs
import requests
from packaging import version
from PyQt6.QtCore import QUrl, Qt, QObject, pyqtSlot, QSharedMemory, QSystemSemaphore, QByteArray
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMenu, QSystemTrayIcon, QMessageBox
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
from PyQt6.QtGui import QIcon, QDragEnterEvent, QDropEvent, QDragMoveEvent, QCloseEvent
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QDialog, QLabel, QHBoxLayout
import webbrowser


__version__ = "1.2.0"


class MyWebEngineView(QWebEngineView):
    def __init__(self, bridge, dest_folder, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridge = bridge
        self.dest_folder = dest_folder
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops, True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("dragEnterEvent: принимаем событие")
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        print("Python: dropEvent: событие drop получено")
        event.acceptProposedAction()
        mimeData = event.mimeData()
        if mimeData.hasUrls():
            files = [url.toLocalFile() for url in mimeData.urls()]
            if not files:
                return

            drop_point = event.position().toPoint()

            get_folder_type_js = """
            (function(x, y) {
                let element = document.elementFromPoint(x, y);
                let targetFolderType = null;
                let validDropZones = ['rawsList', 'roadsList', 'voiceList', 'subsList'];
                while (element) {
                    if (validDropZones.includes(element.id)) {
                        targetFolderType = element.id.replace('List', '').toLowerCase();
                        return targetFolderType;
                    }
                    element = element.parentElement;
                }
                return null;
            })(%1, %2);
            """.replace("%1", str(drop_point.x())).replace("%2", str(drop_point.y()))

            def handle_js_result(target_folder_type):
                if target_folder_type and target_folder_type in ['raws', 'roads', 'voice', 'subs']:
                    project_name = self.bridge.current_project
                    season = self.bridge.current_season
                    episode = self.bridge.current_episode
                    base_dir = self.bridge.base_dir

                    if not project_name or not season or not episode or not base_dir:
                        print("Проект, сезон или эпизод не выбраны, или базовая директория не установлена.")
                        return

                    project_path = os.path.join(base_dir, project_name)
                    season_folder = f"S{int(season):02d}"
                    episode_folder = f"{season_folder}-E{int(episode):02d}"
                    target_folder_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
                    target_folder_name = target_folder_map.get(target_folder_type)

                    if not target_folder_name:
                        print("Неверный тип папки:", target_folder_type)
                        return

                    for file_path in files:
                        filename = os.path.basename(file_path)
                        dest_path = os.path.join(project_path, target_folder_name, season_folder, episode_folder, filename)
                        try:
                            shutil.copy2(file_path, dest_path)
                            print(f"Файл {file_path} скопирован в {dest_path}")
                        except Exception as e:
                            print(f"Ошибка при копировании файла {file_path}: {e}")
                else:
                    print("Неверная зона для Drop")

            self.page().runJavaScript(get_folder_type_js, handle_js_result)

        else:
            print("В dropEvent нет URL")


class Bridge(QObject):
    def __init__(self):
        super().__init__()
        self.base_directories = []
        self.current_base_directory_index = 0
        self.config_path = self._get_config_path()
        self.current_project = ""
        self.current_season = ""
        self.current_episode = ""
        self.loadConfig()

    @property
    def base_dir(self):
        if 0 <= self.current_base_directory_index < len(self.base_directories):
            return self.base_directories[self.current_base_directory_index]
        return None


    def _get_config_path(self):
        config_dir = appdirs.user_config_dir("PMReaper", "Florka")
        os.makedirs(config_dir, exist_ok=True)
        return os.path.join(config_dir, "config.json")

    def loadConfig(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.base_directories = config.get("base_directories", [])
                    self.current_base_directory_index = config.get("current_base_directory_index", 0)
            except Exception as e:
                print("Ошибка загрузки конфигурации:", e)
        else:
            print("Файл конфигурации не найден.")


    def saveConfig(self, base_directories=None, current_base_directory_index=None):
        if base_directories is None:
            base_directories = self.base_directories
        if current_base_directory_index is None:
            current_base_directory_index = self.current_base_directory_index

        print(f"Сохранение конфигурации в: {self.config_path} (AppData)")
        config = {
            "base_directories": base_directories,
            "current_base_directory_index": current_base_directory_index,
        }
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f)
        except Exception as e:
            print("Ошибка сохранения конфигурации:", e)

    @pyqtSlot(str, result=str) # Deprecated
    def setBaseDirectory(self, path): # Deprecated
        if os.path.exists(path) and os.path.isdir(path):
            self.base_directories = [path] # Replace list with new one
            self.current_base_directory_index = 0
            self.saveConfig()
            return "Базовая директория установлена успешно."
        else:
            return "Неверный путь. Папка не существует."

    @pyqtSlot(result=str)
    def browseDirectory(self):
        print("Python: browseDirectory вызвана")  # <--- Добавлено для отладки
        directory = QFileDialog.getExistingDirectory(None, "Выберите папку для проектов", os.path.expanduser("~"))
        if directory:
            return directory
        else:
            return ""

    @pyqtSlot(str, result=str)
    def addBaseDirectory(self, path):
        print(f"Python: addBaseDirectory вызвана с путем: {path}")  # <--- Добавлено для отладки
        if not os.path.exists(path) or not os.path.isdir(path):
            return "Неверный путь. Папка не существует."
        if path in self.base_directories:
            return "Директория уже добавлена."
        self.base_directories.append(path)
        self.saveConfig()
        return "Базовая директория добавлена."

    @pyqtSlot(int, result=str)
    def deleteBaseDirectory(self, index):
        if 0 <= index < len(self.base_directories):
            del self.base_directories[index]
            if self.current_base_directory_index >= len(self.base_directories):
                self.current_base_directory_index = max(0, len(self.base_directories) - 1) # go to last or 0
            self.saveConfig()
            return "Базовая директория удалена."
        return "Индекс вне диапазона."

    @pyqtSlot(int, result=str)
    def setCurrentBaseDirectory(self, index):
        if 0 <= index < len(self.base_directories):
            self.current_base_directory_index = index
            self.saveConfig()
            return "Текущая базовая директория изменена."
        return "Индекс вне диапазона."

    @pyqtSlot(result=str)
    def listBaseDirectories(self):
        try:
            directories = self.base_directories
            return json.dumps(directories)
        except Exception as e:
            return json.dumps([])

    @pyqtSlot(result=str)
    def listProjects(self):
        print("Python: listProjects вызвана")  # <--- Добавлено для отладки
        if not self.base_dir or not os.path.isdir(self.base_dir):
            print("Python: Базовая директория не установлена или не существует.")  # <--- Добавлено для отладки
            return json.dumps([])
        try:
            projects = [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]
            print("Python: Найденные проекты:", projects)  # <--- Добавлено для отладки
            return json.dumps(projects)
        except Exception as e:
            print(f"Python: Ошибка в listProjects: {e}")  # <--- Добавлено для отладки
            return json.dumps([])

    @pyqtSlot(str, result=str)
    def createProject(self, projectName):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if os.path.exists(project_path):
            return "Проект с таким названием уже существует."
        try:
            os.makedirs(project_path)

            os.makedirs(os.path.join(project_path, "reaper"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "source"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "outs"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "raws"), exist_ok=True)
            os.makedirs(os.path.join(project_path, "subs"), exist_ok=True)
            return "Проект создан успешно."
        except Exception as e:
            return f"Ошибка при создании проекта: {str(e)}"

    @pyqtSlot(str, result=str)
    def deleteProject(self, projectName):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path):
            return "Проект не найден."
        try:
            shutil.rmtree(project_path)
            return "Проект удалён."
        except Exception as e:
            return f"Ошибка при удалении проекта: {str(e)}"

    @pyqtSlot(str, result=str)
    def listEpisodes(self, projectName):
        episodes = {}
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return json.dumps(episodes)
        project_path = os.path.join(self.base_dir, projectName)
        reaper_dir = os.path.join(project_path, "reaper")
        if not os.path.exists(reaper_dir):
            return json.dumps(episodes)
        try:
            for item in os.listdir(reaper_dir):
                season_path = os.path.join(reaper_dir, item)
                if os.path.isdir(season_path) and item.startswith("S") and len(item) == 3:
                    try:
                        season_num = int(item[1:])
                    except:
                        continue
                    episodes[str(season_num)] = []

                    for ep_item in os.listdir(season_path):
                        ep_path = os.path.join(season_path, ep_item)
                        if os.path.isdir(ep_path) and ep_item.startswith(item + "-E"):
                            try:
                                episode_num = int(ep_item.split("-E")[1])
                                episodes[str(season_num)].append(episode_num)
                            except:
                                continue
                    episodes[str(season_num)].sort()
            return json.dumps(episodes)
        except Exception as e:
            return json.dumps({})

    @pyqtSlot(str, int, result=str)
    def addSeason(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path):
            return "Проект не найден."
        season_folder = f"S{season:02d}"
        reaper_season = os.path.join(project_path, "reaper", season_folder)
        if os.path.exists(reaper_season):
            return "Сезон уже существует."
        try:
            for d in ["reaper", "source", "outs", "raws", "subs"]:
                os.makedirs(os.path.join(project_path, d, season_folder), exist_ok=True)
            return "Сезон создан."
        except Exception as e:
            return f"Ошибка при создании сезона: {str(e)}"

    @pyqtSlot(str, int, int, result=str)
    def addEpisode(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        reaper_season = os.path.join(project_path, "reaper", season_folder)
        if not os.path.exists(reaper_season):
            return "Сначала добавьте сезон."
        reaper_episode = os.path.join(reaper_season, episode_folder)
        if os.path.exists(reaper_episode):
            return "Эпизод уже существует."

        try:
            for d in ["reaper", "source", "outs", "raws", "subs"]:
                os.makedirs(os.path.join(project_path, d, season_folder, episode_folder), exist_ok=True)

            rpp_filename = f"{projectName}_{episode_folder}.rpp"
            rpp_filepath = os.path.join(reaper_episode, rpp_filename)

            last_rpp = self.find_last_rpp(project_path, season, episode)
            if last_rpp and os.path.exists(last_rpp):
                shutil.copy(last_rpp, rpp_filepath)
            else:
                with open(rpp_filepath, "w", encoding="utf-8") as f:
                    f.write("")

            return "Эпизод создан."
        except Exception as e:
            return f"Ошибка при добавлении эпизода: {str(e)}"

    def find_last_rpp(self, project_path, season, episode):
        for s in range(season, 0, -1):
            season_folder = f"S{s:02d}"
            season_path = os.path.join(project_path, "reaper", season_folder)
            if os.path.exists(season_path):
                episodes = sorted([d for d in os.listdir(season_path) if d.startswith(season_folder + "-E")], reverse=True)
                if episodes:
                    for last_episode in episodes:
                        rpp_path = os.path.join(season_path, last_episode, f"{os.path.basename(project_path)}_{last_episode}.rpp")
                        if os.path.exists(rpp_path):
                            return rpp_path
        return None

    @pyqtSlot(str, int, int, result=str)
    def deleteEpisode(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        deleted = []
        for d in ["reaper", "source", "outs", "raws", "subs"]:
            ep_path = os.path.join(project_path, d, season_folder, episode_folder)
            if os.path.exists(ep_path):
                try:
                    shutil.rmtree(ep_path)
                    deleted.append(d)
                except Exception as e:
                    return f"Ошибка при удалении эпизода из {d}: {str(e)}"
        return f"Эпизод удалён из: {', '.join(deleted)}."

    @pyqtSlot(str, int, result=str)
    def deleteSeason(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        deleted = []
        for d in ["reaper", "source", "outs", "raws", "subs"]:
            season_path = os.path.join(project_path, d, season_folder)
            if os.path.exists(season_path):
                try:
                    shutil.rmtree(season_path)
                    deleted.append(d)
                except Exception as e:
                    return f"Ошибка при удалении сезона из {d}: {str(e)}"
        return f"Сезон удалён из: {', '.join(deleted)}."

    @pyqtSlot(str, int, int, result=str)
    def openEpisodeFolder(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        ep_path = os.path.join(project_path, "reaper", season_folder, episode_folder)
        if not os.path.exists(ep_path):
            return "Эпизод не найден."
        try:
            os.startfile(ep_path)
            return "Папка эпизода открыта."
        except Exception as e:
            return f"Ошибка при открытии папки эпизода: {str(e)}"

    @pyqtSlot(str, int, result=str)
    def openSeasonFolder(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        season_path = os.path.join(project_path, "reaper", season_folder)
        if not os.path.exists(season_path):
            return "Сезон не найден."
        try:
            os.startfile(season_path)
            return "Папка сезона открыта."
        except Exception as e:
            return f"Ошибка при открытии папки сезона: {str(e)}"

    @pyqtSlot(str, int, int, result=str)
    def openProjectFile(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        rpp_filepath = os.path.join(project_path, "reaper", season_folder, episode_folder, f"{projectName}_{episode_folder}.rpp")
        if not os.path.exists(rpp_filepath):
            return "Файл проекта не найден."
        try:
            os.startfile(rpp_filepath)
            return "Файл проекта открыт."
        except Exception as e:
            return f"Ошибка при открытии файла проекта: {str(e)}"

    @pyqtSlot(str, int, int, result=str)
    def renameSeason(self, projectName, oldSeason, newSeason):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path):
            return "Проект не найден."
        old_season_folder = f"S{oldSeason:02d}"
        new_season_folder = f"S{newSeason:02d}"
        for d in ["reaper", "source", "outs", "raws", "subs"]:
            old_path = os.path.join(project_path, d, old_season_folder)
            new_path = os.path.join(project_path, d, new_season_folder)
            if not os.path.exists(old_path):
                return f"Сезон {oldSeason} не найден в {d}."
            if os.path.exists(new_path):
                return f"Сезон {newSeason} уже существует в {d}."
            try:
                os.rename(old_path, new_path)
            except Exception as e:
                return f"Ошибка при переименовании сезона в {d}: {str(e)}"
        return "Сезон переименован."

    @pyqtSlot(str, int, int, int, result=str)
    def renameEpisode(self, projectName, season, oldEpisode, newEpisode):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        old_episode_folder = f"{season_folder}-E{oldEpisode:02d}"
        new_episode_folder = f"{season_folder}-E{newEpisode:02d}"
        for d in ["reaper", "source", "outs", "raws", "subs"]:
            old_path = os.path.join(project_path, d, season_folder, old_episode_folder)
            new_path = os.path.join(project_path, d, season_folder, new_episode_folder)
            if not os.path.exists(old_path):
                return f"Эпизод {oldEpisode} не найден в {d}."
            if os.path.exists(new_path):
                return f"Эпизод {newEpisode} уже существует в {d}."
            try:
                os.rename(old_path, new_path)
                if d == "reaper":
                    old_rpp = os.path.join(new_path, f"{projectName}_{old_episode_folder}.rpp")
                    new_rpp = os.path.join(new_path, f"{projectName}_{new_episode_folder}.rpp")
                    if os.path.exists(old_rpp):
                        os.rename(old_rpp, new_rpp)
            except Exception as e:
                return f"Ошибка при переименовании эпизода в {d}: {str(e)}"
        return "Эпизод переименован."

    @pyqtSlot(str, int, int, result=str)
    def listFolderContent(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return json.dumps({})
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        content = {}
        folder_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
        for folderType, folder_name in folder_map.items():
            folder_path = os.path.join(project_path, folder_name, season_folder, episode_folder)
            if os.path.exists(folder_path):
                try:
                    files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
                    content[folderType] = files
                except Exception as e:
                    content[folderType] = ["Ошибка чтения папки"]
            else:
                content[folderType] = []
        return json.dumps(content)

    @pyqtSlot(str, int, int, str, result=str)
    def openFolderForType(self, projectName, season, episode, folderType):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        folder_name_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
        folder_name = folder_name_map.get(folderType)
        if not folder_name:
            return "Неверный тип папки."

        folder_path = os.path.join(project_path, folder_name, season_folder, episode_folder)

        if not os.path.exists(folder_path):
            return "Папка не найдена."
        try:
            os.startfile(folder_path)
            return f"Папка {folderType} открыта."
        except Exception as e:
            return f"Ошибка при открытии папки {folderType}: {str(e)}"

    @pyqtSlot(str, int, int, str, str, result=str)
    def moveFileToFolder(self, projectName, season, episode, sourceFolderType, targetFolderType, filename):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        folder_name_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}

        source_folder_name = folder_name_map.get(sourceFolderType)
        target_folder_name = folder_name_map.get(targetFolderType)

        if not source_folder_name or not target_folder_name:
            return "Неверный тип папки."

        source_path = os.path.join(project_path, source_folder_name, season_folder, episode_folder, filename)
        target_path = os.path.join(project_path, target_folder_name, season_folder, episode_folder, filename)

        if not os.path.exists(source_path):
            return "Файл не найден в исходной папке."

        try:
            shutil.move(source_path, target_path)
            return "Файл перемещён."
        except Exception as e:
            return f"Ошибка при перемещении файла: {str(e)}"

    @pyqtSlot(str, int, int, str, str, str, result=str)
    def uploadFileToFolder(self, projectName, season, episode, folderType, filePath, filename):
        if not self.base_dir or not os.path.isdir(self.base_dir): # Check if base_dir is valid
            return "Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"
        folder_name_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
        target_folder_name = folder_name_map.get(folderType)

        if not target_folder_name:
            return "Неверный тип папки."

        target_path = os.path.join(project_path, target_folder_name, season_folder, episode_folder, filename)

        if not os.path.exists(os.path.dirname(target_path)):
            return "Папка назначения не найдена."

        if not os.path.exists(filePath):
            return "Исходный файл не найден."

        try:
            shutil.copy2(filePath, target_path)
            return "Файл загружен."
        except Exception as e:
            return f"Ошибка при загрузке файла: {str(e)}"

    @pyqtSlot(str)
    def setCurrentProject(self, projectName):
        print(f"Python: setCurrentProject called, projectName: {projectName}")
        self.current_project = projectName

    @pyqtSlot(str, str)
    def setCurrentSeasonEpisode(self, season, episode):
        print(f"Python: setCurrentSeasonEpisode called, season: {season}, episode: {episode}")
        try:
            self.current_season = season
            self.current_episode = episode
        except ValueError:
            print("Error: Season or episode is not a valid number")


GITHUB_REPO_URL = "https://github.com/Floriddd/PMReaper.git"
GITHUB_API_URL = "https://api.github.com/repos/Floriddd/PMReaper/releases/latest"
GITHUB_RELEASES_URL = "https://github.com/Floriddd/PMReaper/releases/latest"

class UpdateDialog(QDialog):
    def __init__(self, latest_version, download_url, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Доступно обновление")
        self.download_url = download_url

        layout = QVBoxLayout(self)
        label = QLabel(f"Доступна новая версия: {latest_version}.\nХотите скачать обновление?")
        layout.addWidget(label)

        button_layout = QHBoxLayout()
        update_button = QPushButton("Скачать", self)
        update_button.clicked.connect(self.start_download)
        button_layout.addWidget(update_button)

        cancel_button = QPushButton("Отмена", self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def start_download(self):
        print(f"Начинаем скачивание с URL: {self.download_url}")
        try:
            webbrowser.open(self.download_url)
            self.accept()
        except Exception as e:
            print(f"Ошибка при открытии URL для скачивания: {e}")
            QMessageBox.critical(self, "Ошибка", f"Не удалось открыть ссылку для скачивания в браузере: {e}")


class MainWindow(QMainWindow):
    def __init__(self, bridge, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridge = bridge
        self.setWindowTitle("PMReaper (by FlorkA)")
        self.setFixedSize(1000, 700)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "ui", "favicon.ico")))

        self.channel = QWebChannel()
        self.channel.registerObject("pyBridge", self.bridge)

        dest_folder = os.path.join(os.getcwd(), "dropped_files")
        os.makedirs(dest_folder, exist_ok=True)

        self.view = MyWebEngineView(self.bridge, dest_folder, self)
        self.view.page().setWebChannel(self.channel)

        ui_path = os.path.join(os.path.dirname(__file__), "ui", "index.html")
        url = QUrl.fromLocalFile(os.path.abspath(ui_path))
        self.view.load(url)

        self.setCentralWidget(self.view)

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "ui", "favicon.ico")))
        self.tray_icon.activated.connect(self.tray_icon_activated)

        tray_menu = QMenu()
        open_action = tray_menu.addAction("Открыть")
        open_action.triggered.connect(self.show_window_from_tray)
        check_update_action = tray_menu.addAction("Проверить обновления")
        check_update_action.triggered.connect(self.check_for_updates)
        close_action = tray_menu.addAction("Закрыть")
        close_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addSeparator()
        version_action = tray_menu.addAction(f"Версия: {__version__}")
        version_action.setEnabled(False)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.setToolTip("PMReaper")

        self.show()

        self.check_for_updates(on_startup=True)


    def closeEvent(self, event: QCloseEvent):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "PMReaper",
            "Приложение свернуто в трей.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )


    def tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger or reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show_window_from_tray()

    def show_window_from_tray(self):
        self.showNormal()
        self.activateWindow()
        self.raise_()


    def raise_(self):
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()

    def check_for_updates(self, on_startup=False):
        try:
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()
            release_info = response.json()
            latest_version_tag = release_info.get("tag_name")
            latest_version = latest_version_tag.lstrip('v') if latest_version_tag else None

            assets = release_info.get("assets", [])
            download_url = None
            if assets:
                download_url = assets[0].get("browser_download_url")

            if latest_version and download_url:
                current_version = __version__

                if version.parse(latest_version) > version.parse(current_version):
                    dialog = UpdateDialog(latest_version, download_url, self)
                    dialog.exec()
                else:
                    if not on_startup:
                        QMessageBox.information(self, "Обновления", "У вас установлена последняя версия.")
            else:
                QMessageBox.warning(self, "Ошибка обновления", "Не удалось получить информацию о последней версии или ссылку на скачивание.")

        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка обновления", f"Ошибка при проверке обновлений: {e}")
        except json.JSONDecodeError:
            QMessageBox.critical(self, "Ошибка обновления", "Не удалось обработать ответ сервера обновлений.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка обновления", f"Неизвестная ошибка при проверке обновлений: {e}")



def main():
    if hasattr(sys, '_MEIPASS'):
        os.chdir(sys._MEIPASS)

    app = QApplication(sys.argv)

    shared_memory_key = "pmreaper_single_instance_key"
    shared_memory = QSharedMemory(shared_memory_key)
    if shared_memory.attach():
        QMessageBox.information(None, "PMReaper", "Приложение уже запущено и находится в трее.")
        return 0
    else:
        shared_memory.create(1)

    bridge = Bridge()
    window = MainWindow(bridge)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()