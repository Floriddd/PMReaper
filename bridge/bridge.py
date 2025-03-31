import os
import json
import shutil
import appdirs
import sys
import ctypes
import subprocess
import tempfile
from PyQt6.QtCore import pyqtSlot, QObject, QFileSystemWatcher, pyqtSignal
from PyQt6.QtWidgets import QFileDialog

class Bridge(QObject):
    filesChanged = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.file_watcher = QFileSystemWatcher()
        self.file_watcher.directoryChanged.connect(self.on_files_changed)
        self.file_watcher.fileChanged.connect(self.on_files_changed)
        self.base_directories = []
        self.current_base_directory_index = 0
        self.config_path = self._get_config_path()
        self.current_project = ""
        self.current_season = ""
        self.current_episode = ""
        self.loadConfig()

    def on_files_changed(self, path):
        print(f"Файлы изменились в: {path}")
        self.filesChanged.emit()

    def watch_folders(self, project_name, season, episode):
        if not self.base_dir:
            return
        folders = {
            "raws": "raws",
            "roads": "outs",
            "voice": "source",
            "subs": "subs"
        }
        base_path = os.path.join(self.base_dir, project_name, f"S{int(season):02d}",
                                 f"S{int(season):02d}-E{int(episode):02d}")
        for key, subfolder in folders.items():
            folder_path = os.path.join(base_path, subfolder)
            if os.path.exists(folder_path):
                self.file_watcher.addPath(folder_path)
                print(f"[DEBUG] Отслеживаем папку: {folder_path}")

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
                print("[DEBUG] Ошибка загрузки конфигурации:", e)
        else:
            print("[DEBUG] Файл конфигурации не найден.")

    def saveConfig(self, base_directories=None, current_base_directory_index=None):
        if base_directories is None:
            base_directories = self.base_directories
        if current_base_directory_index is None:
            current_base_directory_index = self.current_base_directory_index

        print(f"[DEBUG] Сохранение конфигурации в: {self.config_path} (AppData)")
        config = {
            "base_directories": base_directories,
            "current_base_directory_index": current_base_directory_index,
        }

        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    existing_config = json.load(f)
                    if "settings" in existing_config:
                        config["settings"] = existing_config["settings"]
            except Exception as e:
                print("[DEBUG] Ошибка при загрузке существующей конфигурации:", e)
        
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            print("[DEBUG] Конфигурация сохранена.")
            return True
        except Exception as e:
            print("[DEBUG] Ошибка сохранения конфигурации:", e)
            return False
            
    @pyqtSlot(str, result=str)
    def loadSettings(self, callback):
        """
        Загружает настройки приложения из файла конфигурации
        """
        print("[DEBUG] Загрузка настроек приложения")
        
        settings_json = "{}"
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    settings = config.get("settings", {})
                    print(f"[DEBUG] Загружены настройки: {settings}")
                    settings_json = json.dumps(settings)
            except Exception as e:
                print("[DEBUG] Ошибка загрузки настроек:", e)
        else:
            print("[DEBUG] Файл конфигурации не найден при загрузке настроек")
        return settings_json
    
    @pyqtSlot(str, result=bool)
    def saveSettings(self, settings_json):
        """
        Сохраняет настройки приложения в файл конфигурации
        """
        print(f"[DEBUG] Сохранение настроек приложения: {settings_json}")
        
        try:
            settings = json.loads(settings_json)
            config = {}
            if os.path.exists(self.config_path):
                try:
                    with open(self.config_path, "r", encoding="utf-8") as f:
                        config = json.load(f)
                except Exception as e:
                    print("[DEBUG] Ошибка при загрузке существующей конфигурации:", e)

            config["settings"] = settings

            if "base_directories" not in config:
                config["base_directories"] = self.base_directories
            if "current_base_directory_index" not in config:
                config["current_base_directory_index"] = self.current_base_directory_index

            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
            
            print("[DEBUG] Настройки приложения сохранены")
            return True
        except Exception as e:
            print(f"[DEBUG] Ошибка сохранения настроек: {e}")
            return False

    @pyqtSlot(result=str)
    def browseDirectory(self):
        print("[DEBUG] Python: browseDirectory вызвана")
        directory = QFileDialog.getExistingDirectory(None, "[DEBUG] Выберите папку для проектов", os.path.expanduser("~"))
        if directory:
            return directory
        else:
            return ""

    @pyqtSlot(str, result=str)
    def addBaseDirectory(self, path):
        print(f"[DEBUG] Python: addBaseDirectory вызвана с путем: {path}")
        if not os.path.exists(path) or not os.path.isdir(path):
            return "[DEBUG] Неверный путь. Папка не существует."
        if path in self.base_directories:
            return "[DEBUG] Директория уже добавлена."
        self.base_directories.append(path)
        self.saveConfig()
        return "[DEBUG] Базовая директория добавлена."

    @pyqtSlot(int, result=str)
    def deleteBaseDirectory(self, index):
        if 0 <= index < len(self.base_directories):
            del self.base_directories[index]
            if self.current_base_directory_index >= len(self.base_directories):
                self.current_base_directory_index = max(0, len(self.base_directories) - 1)
            self.saveConfig()
            return "[DEBUG] Базовая директория удалена."
        return "[DEBUG] Индекс вне диапазона."

    @pyqtSlot(int, result=str)
    def setCurrentBaseDirectory(self, index):
        if 0 <= index < len(self.base_directories):
            self.current_base_directory_index = index
            self.saveConfig()
            return "[DEBUG] Текущая базовая директория изменена."
        return "[DEBUG] Индекс вне диапазона."

    @pyqtSlot(result=str)
    def listBaseDirectories(self):
        try:
            return json.dumps(self.base_directories)
        except Exception as e:
            print("[DEBUG] Ошибка при формировании списка базовых директорий:", e)
            return json.dumps([])

    @pyqtSlot(result=str)
    def listProjects(self):
        print("[DEBUG] Python: listProjects вызвана")
        if not self.base_dir or not os.path.isdir(self.base_dir):
            print("[DEBUG] Базовая директория не установлена или не существует.")
            return json.dumps([])
        try:
            projects = [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]
            print("[DEBUG] Найденные проекты:", projects)
            return json.dumps(projects)
        except Exception as e:
            print(f"[DEBUG] Ошибка в listProjects: {e}")
            return json.dumps([])

    @pyqtSlot(str, result=str)
    def createProject(self, projectName):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if os.path.exists(project_path):
            return "[DEBUG] Проект с таким названием уже существует."
        try:
            os.makedirs(project_path)
            return "[DEBUG] Проект создан успешно."
        except Exception as e:
            return f"[DEBUG] Ошибка при создании проекта: {str(e)}"

    @pyqtSlot(str, result=str)
    def deleteProject(self, projectName):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path):
            return "[DEBUG] Проект не найден."
        try:
            shutil.rmtree(project_path)
            return "[DEBUG] Проект удалён."
        except Exception as e:
            return f"[DEBUG] Ошибка при удалении проекта: {str(e)}"

    @pyqtSlot(str, result=str)
    def setBaseDirectory(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.base_directories = [path]
            self.current_base_directory_index = 0
            self.saveConfig()
            return "[DEBUG] Базовая директория установлена успешно."
        else:
            return "[DEBUG] Неверный путь. Папка не существует."

    @pyqtSlot(str, result=str)
    def listEpisodes(self, projectName):
        episodes = {}
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return json.dumps(episodes)
        project_path = os.path.join(self.base_dir, projectName)

        if not os.path.exists(project_path):
            return json.dumps(episodes)

        try:
            for item in os.listdir(project_path):
                season_path = os.path.join(project_path, item)
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
                                if os.path.exists(os.path.join(ep_path, "reaper")):
                                    episodes[str(season_num)].append(episode_num)
                            except:
                                continue
                    episodes[str(season_num)].sort()
            return json.dumps(episodes)
        except Exception as e:
            print(f"[DEBUG] Ошибка в listEpisodes: {e}")
            return json.dumps({})

    @pyqtSlot(str, int, result=str)
    def addSeason(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path):
            return "[DEBUG] Проект не найден."
        season_folder = f"S{season:02d}"
        season_path = os.path.join(project_path, season_folder)
        if os.path.exists(season_path):
            return "[DEBUG] Сезон уже существует."
        try:
            os.makedirs(season_path, exist_ok=True)
            return "[DEBUG] Сезон создан."
        except Exception as e:
            return f"[DEBUG] Ошибка при создании сезона: {str(e)}"

    @pyqtSlot(str, int, int, result=str)
    def addEpisode(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        season_path = os.path.join(project_path, season_folder)
        if not os.path.exists(season_path):
            return "[DEBUG] Сначала добавьте сезон."

        episode_path = os.path.join(season_path, episode_folder)
        if os.path.exists(episode_path):
            return "[DEBUG] Эпизод уже существует."

        try:
            os.makedirs(episode_path, exist_ok=True)
            for d in ["reaper", "source", "outs", "raws", "subs"]:
                os.makedirs(os.path.join(episode_path, d), exist_ok=True)

            rpp_filename = f"{projectName}_{episode_folder}.rpp"
            rpp_filepath = os.path.join(episode_path, "reaper", rpp_filename)

            last_rpp = self.find_last_rpp(project_path, season, episode)
            if last_rpp and os.path.exists(last_rpp):
                shutil.copy(last_rpp, rpp_filepath)
            else:
                with open(rpp_filepath, "w", encoding="utf-8") as f:
                    f.write("")
            return "[DEBUG] Эпизод создан."
        except Exception as e:
            return f"[DEBUG] Ошибка при добавлении эпизода: {str(e)}"

    def find_last_rpp(self, project_path, season, episode):
        for s in range(season, 0, -1):
            season_folder = f"S{s:02d}"
            season_path = os.path.join(project_path, season_folder)
            if os.path.exists(season_path):
                episodes = sorted([d for d in os.listdir(season_path) if d.startswith(season_folder + "-E")],
                                  reverse=True)
                if episodes:
                    for last_episode in episodes:
                        rpp_path = os.path.join(season_path, last_episode, "reaper",
                                                f"{os.path.basename(project_path)}_{last_episode}.rpp")
                        if os.path.exists(rpp_path):
                            return rpp_path
        return None

    @pyqtSlot(str, int, int, result=str)
    def deleteEpisode(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        episode_path = os.path.join(project_path, season_folder, episode_folder)
        if os.path.exists(episode_path):
            try:
                shutil.rmtree(episode_path)
                return f"Эпизод удалён."
            except Exception as e:
                return f"Ошибка при удалении эпизода: {str(e)}"
        return "Эпизод не найден."

    @pyqtSlot(str, int, result=str)
    def deleteSeason(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"

        season_path = os.path.join(project_path, season_folder)
        if os.path.exists(season_path):
            try:
                shutil.rmtree(season_path)
                return f"[DEBUG] Сезон удалён."
            except Exception as e:
                return f"[DEBUG] Ошибка при удалении сезона: {str(e)}"
        return "[DEBUG] Сезон не найден."

    @pyqtSlot(str, int, int, result=str)
    def openEpisodeFolder(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        ep_path = os.path.join(project_path, season_folder, episode_folder)
        if not os.path.exists(ep_path):
            return "[DEBUG] Эпизод не найден."
        try:
            os.startfile(ep_path)
            return "[DEBUG] Папка эпизода открыта."
        except Exception as e:
            return f"[DEBUG] Ошибка при открытии папки эпизода: {str(e)}"

    @pyqtSlot(str, int, result=str)
    def openSeasonFolder(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"

        season_path = os.path.join(project_path, season_folder)
        if not os.path.exists(season_path):
            return "[DEBUG] Сезон не найден."
        try:
            os.startfile(season_path)
            return "[DEBUG] Папка сезона открыта."
        except Exception as e:
            return f"[DEBUG] Ошибка при открытии папки сезона: {str(e)}"

    @pyqtSlot(str, int, int, result=str)
    def openProjectFile(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        rpp_filepath = os.path.join(project_path, season_folder, episode_folder, "reaper",
                                    f"{projectName}_{episode_folder}.rpp")
        if not os.path.exists(rpp_filepath):
            return "[DEBUG] Файл проекта не найден."
        try:
            os.startfile(rpp_filepath)
            return "[DEBUG] Файл проекта открыт."
        except Exception as e:
            return f"[DEBUG] Ошибка при открытии файла проекта: {str(e)}"

    @pyqtSlot(str, int, int, int, result=str)
    def renameSeason(self, projectName, oldSeason, newSeason):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path):
            return "[DEBUG] Проект не найден."
        old_season_folder = f"S{oldSeason:02d}"
        new_season_folder = f"S{newSeason:02d}"

        old_path = os.path.join(project_path, old_season_folder)
        new_path = os.path.join(project_path, new_season_folder)

        if not os.path.exists(old_path):
            return f"[DEBUG] Сезон {oldSeason} не найден."
        if os.path.exists(new_path):
            return f"[DEBUG] Сезон {newSeason} уже существует."

        try:
            os.rename(old_path, new_path)

            for item in os.listdir(new_path):
                if item.startswith(old_season_folder + "-E"):
                    old_ep_path = os.path.join(new_path, item)
                    new_ep_name = item.replace(old_season_folder, new_season_folder)
                    new_ep_path = os.path.join(new_path, new_ep_name)
                    os.rename(old_ep_path, new_ep_path)

                    reaper_folder = os.path.join(new_ep_path, "reaper")
                    if os.path.exists(reaper_folder):
                        for file in os.listdir(reaper_folder):
                            if file.endswith(".rpp") and old_season_folder in file:
                                old_file_path = os.path.join(reaper_folder, file)
                                new_file_name = file.replace(old_season_folder, new_season_folder)
                                new_file_path = os.path.join(reaper_folder, new_file_name)
                                os.rename(old_file_path, new_file_path)
        except Exception as e:
            return f"[DEBUG] Ошибка при переименовании сезона: {str(e)}"

        return "[DEBUG] Сезон переименован."

    @pyqtSlot(str, int, int, int, result=str)
    def renameEpisode(self, projectName, season, oldEpisode, newEpisode):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        old_episode_folder = f"{season_folder}-E{oldEpisode:02d}"
        new_episode_folder = f"{season_folder}-E{newEpisode:02d}"

        old_path = os.path.join(project_path, season_folder, old_episode_folder)
        new_path = os.path.join(project_path, season_folder, new_episode_folder)

        if not os.path.exists(old_path):
            return f"[DEBUG] Эпизод {oldEpisode} не найден."
        if os.path.exists(new_path):
            return f"[DEBUG] Эпизод {newEpisode} уже существует."

        try:
            os.rename(old_path, new_path)

            reaper_folder = os.path.join(new_path, "reaper")
            if os.path.exists(reaper_folder):
                for file in os.listdir(reaper_folder):
                    if file.endswith(".rpp") and old_episode_folder in file:
                        old_file_path = os.path.join(reaper_folder, file)
                        new_file_name = file.replace(old_episode_folder, new_episode_folder)
                        new_file_path = os.path.join(reaper_folder, new_file_name)
                        os.rename(old_file_path, new_file_path)
        except Exception as e:
            return f"[DEBUG] Ошибка при переименовании эпизода: {str(e)}"

        return "[DEBUG] Эпизод переименован."

    @pyqtSlot(str, int, int, result=str)
    def listFolderContent(self, projectName, season, episode):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return json.dumps({})
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        episode_path = os.path.join(project_path, season_folder, episode_folder)
        content = {}
        folder_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}

        for folderType, folder_name in folder_map.items():
            folder_path = os.path.join(episode_path, folder_name)
            if os.path.exists(folder_path):
                try:
                    files = [{"name": f, "path": os.path.join(folder_path, f)}
                             for f in os.listdir(folder_path)
                             if os.path.isfile(os.path.join(folder_path, f))]
                    content[folderType] = files
                except Exception as e:
                    content[folderType] = []
            else:
                content[folderType] = []

        return json.dumps(content)

    @pyqtSlot(str, int, int, str, result=str)
    def openFolderForType(self, projectName, season, episode, folderType):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        folder_name_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
        folder_name = folder_name_map.get(folderType)

        if not folder_name:
            return "[DEBUG] Неверный тип папки."

        folder_path = os.path.join(project_path, season_folder, episode_folder, folder_name)
        if not os.path.exists(folder_path):
            return "[DEBUG] Папка не найдена."
            
        try:
            os.startfile(folder_path)
            return f"[DEBUG] Папка {folderType} открыта."
        except Exception as e:
            return f"[DEBUG] Ошибка при открытии папки {folderType}: {str(e)}"

    @pyqtSlot(str, str, str, result=str)
    def getFilesByType(self, projectName, season, episode):
        """
        Получает файлы из разных папок для отображения в правой панели
        Используется в обновленном UI
        """
        print(f"[DEBUG] getFilesByType вызван для проекта: {projectName}, сезон: {season}, эпизод: {episode}")
        
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return json.dumps({})
            
        try:
            season_num = int(season)
            episode_num = int(episode)
        except ValueError:
            print(f"[DEBUG] Ошибка в getFilesByType: некорректный формат сезона/эпизода")
            return json.dumps({})
            
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season_num:02d}"
        episode_folder = f"{season_folder}-E{episode_num:02d}"
        episode_path = os.path.join(project_path, season_folder, episode_folder)
        
        if not os.path.exists(episode_path):
            print(f"[DEBUG] Путь не существует: {episode_path}")
            return json.dumps({})
            
        result = {
            "raws": [],
            "roads": [],
            "voice": [],
            "subs": []
        }
        
        folder_mapping = {
            "raws": "raws",
            "roads": "outs",
            "voice": "source",
            "subs": "subs"
        }
        
        for key, folder_name in folder_mapping.items():
            folder_path = os.path.join(episode_path, folder_name)
            if os.path.exists(folder_path):
                try:
                    for file_name in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, file_name)
                        if os.path.isfile(file_path):
                            result[key].append(file_path)
                except Exception as e:
                    print(f"[DEBUG] Ошибка при чтении папки {folder_path}: {e}")
        
        self.watch_folders(projectName, season_num, episode_num)
        return json.dumps(result)
        
    @pyqtSlot(str, str, result=str)
    def openFile(self, filePath):
        """
        Открывает файл в ассоциированной программе
        """
        if not os.path.exists(filePath):
            print(f"[DEBUG] Файл не существует: {filePath}")
            return "error"
            
        try:
            os.startfile(filePath)
            return "success"
        except Exception as e:
            print(f"[DEBUG] Ошибка при открытии файла: {e}")
            return "error"
            
    @pyqtSlot(str, str, str, str, str, result=str)
    def moveFile(self, sourcePath, targetType, projectName, season, episode):
        """
        Перемещает файл между папками
        """
        print(f"[DEBUG] moveFile: {sourcePath} -> {targetType}")
        
        if not os.path.exists(sourcePath):
            return "error:file_not_exist"
            
        try:
            season_num = int(season)
            episode_num = int(episode)
        except ValueError:
            return "error:invalid_season_episode"
            
        folder_mapping = {
            "raws": "raws",
            "roads": "outs",
            "voice": "source",
            "subs": "subs"
        }
        
        if targetType not in folder_mapping:
            return "error:invalid_target_type"
            
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season_num:02d}"
        episode_folder = f"{season_folder}-E{episode_num:02d}"
        
        target_folder = os.path.join(project_path, season_folder, episode_folder, folder_mapping[targetType])
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)
            
        filename = os.path.basename(sourcePath)
        target_path = os.path.join(target_folder, filename)
        
        try:
            shutil.move(sourcePath, target_path)
            self.filesChanged.emit()
            return "success"
        except Exception as e:
            print(f"[DEBUG] Ошибка при перемещении файла: {e}")
            return f"error:{str(e)}"
    
    @pyqtSlot(str, str)
    def dragDropFile(self, filePath, targetType):
        """
        Обрабатывает перетаскивание файла из файловой системы
        """
        print(f"[DEBUG] dragDropFile: {filePath} -> {targetType}")
        
        if not self.current_project or not self.current_season or not self.current_episode:
            print("[DEBUG] Не выбран проект, сезон или эпизод")
            return
            
        folder_mapping = {
            "raws": "raws",
            "roads": "outs",
            "voice": "source",
            "subs": "subs"
        }
        
        if targetType not in folder_mapping:
            print(f"[DEBUG] Неверный тип папки: {targetType}")
            return
            
        try:
            season_num = int(self.current_season)
            episode_num = int(self.current_episode)
        except ValueError:
            print("[DEBUG] Некорректный формат сезона/эпизода")
            return
            
        project_path = os.path.join(self.base_dir, self.current_project)
        season_folder = f"S{season_num:02d}"
        episode_folder = f"{season_folder}-E{episode_num:02d}"
        
        target_folder = os.path.join(project_path, season_folder, episode_folder, folder_mapping[targetType])
        
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)
            
        filename = os.path.basename(filePath)
        target_path = os.path.join(target_folder, filename)
        
        try:
            shutil.move(filePath, target_path)
            self.filesChanged.emit()
        except Exception as e:
            print(f"[DEBUG] Ошибка при перемещении файла: {e}")
            
    @pyqtSlot(str, int, int, str, str, str, result=str)
    def moveFileToFolder(self, projectName, season, episode, sourceFolderType, targetFolderType, filename):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        folder_name_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
        source_folder_name = folder_name_map.get(sourceFolderType)
        target_folder_name = folder_name_map.get(targetFolderType)
        
        if not source_folder_name or not target_folder_name:
            return "[DEBUG] Неверный тип папки."

        episode_path = os.path.join(project_path, season_folder, episode_folder)
        source_path = os.path.join(episode_path, source_folder_name, filename)
        target_path = os.path.join(episode_path, target_folder_name, filename)

        if not os.path.exists(source_path):
            return "[DEBUG] Файл не найден в исходной папке."
        
        try:
            shutil.move(source_path, target_path)
            return "[DEBUG] Файл перемещён."
        except Exception as e:
            return f"[DEBUG] Ошибка при перемещении файла: {str(e)}"
    
    @pyqtSlot(str, int, int, str, str, str, result=str)
    def uploadFileToFolder(self, projectName, season, episode, folderType, filePath, filename):
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        season_folder = f"S{season:02d}"
        episode_folder = f"{season_folder}-E{episode:02d}"

        folder_name_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
        target_folder_name = folder_name_map.get(folderType)

        if not target_folder_name:
            return "[DEBUG] Неверный тип папки."

        episode_path = os.path.join(project_path, season_folder, episode_folder)
        target_path = os.path.join(episode_path, target_folder_name, filename)
        
        if not os.path.exists(os.path.dirname(target_path)):
            return "[DEBUG] Папка назначения не найдена."

        if not os.path.exists(filePath):
            return "[DEBUG] Исходный файл не найден."
        
        try:
            shutil.copy2(filePath, target_path)
            return "[DEBUG] Файл загружен."
        except Exception as e:
            return f"[DEBUG] Ошибка при загрузке файла: {str(e)}"
            
    @pyqtSlot(str)
    def setCurrentProject(self, projectName):
        print("[DEBUG] setCurrentProject called with:", projectName)
        if not projectName:
            print("[DEBUG] Ошибка: получено пустое имя проекта!")
        else:
            print("[DEBUG] Проект до установки:", self.current_project)
        self.current_project = projectName
        print("[DEBUG] Текущий проект теперь:", self.current_project)

    @pyqtSlot(str, str)
    def setCurrentSeasonEpisode(self, season, episode):
        print("[DEBUG] setCurrentSeasonEpisode called, season:", season, "episode:", episode)
        try:
            self.current_season = season
            self.current_episode = episode
            self.watch_folders(self.current_project, season, episode)
        except ValueError:
            print("[DEBUG] Ошибка: Season или episode не является числом")

    @pyqtSlot(str, result=str)
    def convertProjectStructure(self, projectName):
        print(f"[DEBUG] convertProjectStructure called for project: {projectName}")
        if not self.base_dir or not os.path.isdir(self.base_dir):
            return "[DEBUG] Сначала установите базовую директорию."
        project_path = os.path.join(self.base_dir, projectName)
        if not os.path.exists(project_path) or not os.path.isdir(project_path):
            return "[DEBUG] Проект не найден."

        old_structure_folders = ["outs", "raws", "reaper", "source", "subs"]
        try:
            for old_top_folder_name in old_structure_folders:
                old_top_folder_path = os.path.join(project_path, old_top_folder_name)
                if not os.path.exists(old_top_folder_path) or not os.path.isdir(old_top_folder_path):
                    print(
                        f"[DEBUG] Warning: Old top folder {old_top_folder_path} does not exist or is not a directory, skipping.")
                    continue

                print(f"[DEBUG] Processing old top folder: {old_top_folder_name}")

                for season_folder_name in os.listdir(old_top_folder_path):
                    season_path_old_struct = os.path.join(old_top_folder_path, season_folder_name)
                    if os.path.isdir(season_path_old_struct) and season_folder_name.startswith("S") and len(
                            season_folder_name) == 3:
                        season_num = season_folder_name[1:]
                        print(f"[DEBUG] Processing season folder: {season_folder_name} in {old_top_folder_name}")

                        for episode_folder_name in os.listdir(season_path_old_struct):
                            if episode_folder_name.startswith(season_folder_name + "-E") and os.path.isdir(
                                    os.path.join(season_path_old_struct, episode_folder_name)):
                                episode_num = episode_folder_name.split("-E")[1]
                                old_episode_path = os.path.join(season_path_old_struct, episode_folder_name)
                                new_episode_path = os.path.join(project_path, season_folder_name, episode_folder_name,
                                                                old_top_folder_name)
                                print(
                                    f"[DEBUG] Processing episode folder: {episode_folder_name} in {season_folder_name} of {old_top_folder_name}, new episode path: {new_episode_path}")

                                if not os.path.exists(new_episode_path):
                                    os.makedirs(new_episode_path, exist_ok=True)
                                    print(f"[DEBUG] Created new folder in new structure: {new_episode_path}")
                                else:
                                    print(f"[DEBUG] New folder in new structure already exists: {new_episode_path}")

                                for file_name in os.listdir(old_episode_path):
                                    old_file_path = os.path.join(old_episode_path, file_name)
                                    new_file_path = os.path.join(new_episode_path, file_name)
                                    print(
                                        f"[DEBUG] Found file: {file_name}, old path: {old_file_path}, new path: {new_file_path}")
                                    if os.path.isfile(old_file_path):
                                        try:
                                            shutil.move(old_file_path, new_file_path)
                                            print(
                                                f"[DEBUG] MOVED file: {file_name} from {old_file_path} to {new_file_path}")
                                        except Exception as move_e:
                                            print(f"[DEBUG] Error moving file {file_name}: {move_e}")
                                    else:
                                        print(f"[DEBUG] Warning: {old_file_path} is not a file, skipping.")

            old_folder = os.path.join(project_path, "_old")
            if not os.path.exists(old_folder):
                os.makedirs(old_folder, exist_ok=True)
                print(f"[DEBUG] Created _old folder: {old_folder}")
            else:
                print(f"[DEBUG] _old folder already exists: {old_folder}")

            for old_top_folder_name in old_structure_folders:
                old_top_folder_path = os.path.join(project_path, old_top_folder_name)
                if os.path.exists(old_top_folder_path) and os.path.isdir(old_top_folder_path):
                    target_old_folder_path = os.path.join(old_folder, old_top_folder_name)
                    try:
                        shutil.move(old_top_folder_path, target_old_folder_path)
                        print(f"[DEBUG] MOVED old top folder {old_top_folder_name} to _old folder.")
                    except Exception as move_top_folder_e:
                        print(f"[DEBUG] Error moving old top folder {old_top_folder_name} to _old: {move_top_folder_e}")

            return "[DEBUG] Структура проекта конвертирована, старые папки перемещены в _old."
        except Exception as e:
            return f"[DEBUG] Ошибка конвертации структуры проекта: {str(e)}"

    @pyqtSlot(str, result=str)
    def getCurrentProject(self, callback):
        """Возвращает текущий проект"""
        self.view.page().runJavaScript(f"{callback}('{self.current_project}')")
        return self.current_project

    @pyqtSlot(str, result=str)
    def getBaseDir(self, callback):
        """Возвращает базовую директорию"""
        self.view.page().runJavaScript(f"{callback}('{self.base_dir}')")
        return self.base_dir

    @pyqtSlot(str, str, result=str)
    def renameProjectFolder(self, oldProjectName, newProjectName):
        """
        Переименовывает папку проекта без потери данных
        """
        print(f"[DEBUG] renameProjectFolder вызвана: {oldProjectName} -> {newProjectName}")
        
        try:
            if not self.base_dir or not os.path.isdir(self.base_dir):
                return "error: Сначала установите базовую директорию."
                
            old_path = os.path.join(self.base_dir, oldProjectName)
            new_path = os.path.join(self.base_dir, newProjectName)
            
            if not os.path.exists(old_path):
                return "error: Проект не найден."
                
            if os.path.exists(new_path):
                return "error: Проект с таким именем уже существует."
            
            # Проверяем открытые файлы в папке перед переименованием
            try:
                for root, dirs, files in os.walk(old_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        try:
                            # Пробуем открыть файл на запись, чтобы проверить, не занят ли он
                            with open(file_path, 'a'):
                                pass
                        except PermissionError:
                            print(f"[DEBUG] Файл {file_path} открыт другим процессом")
                            return "error: Некоторые файлы в проекте открыты другими программами. Закройте все файлы перед переименованием."
            except Exception as e:
                print(f"[DEBUG] Ошибка при проверке открытых файлов: {str(e)}")
                # Продолжаем выполнение, так как это необязательная проверка
                
            # Пытаемся переименовать папку проекта
            try:
                os.rename(old_path, new_path)
                print(f"[DEBUG] Папка проекта переименована: {old_path} -> {new_path}")
            except (PermissionError, OSError) as e:
                print(f"[DEBUG] Ошибка доступа при попытке переименовать {old_path}: {str(e)}")
                
                # Собираем информацию о файлах .rpp для переименования
                files_to_rename = []
                for season_folder in [d for d in os.listdir(old_path) if os.path.isdir(os.path.join(old_path, d)) and d.startswith("S")]:
                    season_path = os.path.join(old_path, season_folder)
                    for episode_folder in [d for d in os.listdir(season_path) if os.path.isdir(os.path.join(season_path, d)) and d.startswith(season_folder + "-E")]:
                        reaper_path = os.path.join(season_path, episode_folder, "reaper")
                        if os.path.exists(reaper_path):
                            for file in os.listdir(reaper_path):
                                if file.endswith(".rpp") and file.startswith(oldProjectName):
                                    old_file_path = os.path.join(reaper_path, file)
                                    new_file_name = file.replace(oldProjectName, newProjectName, 1)
                                    new_file_path = os.path.join(reaper_path, new_file_name)
                                    files_to_rename.append((old_file_path, new_file_path))
                
                # Пытаемся выполнить операцию с правами администратора
                success, message = self.elevate_privileges('rename', {
                    'old_path': old_path,
                    'new_path': new_path,
                    'files_to_rename': files_to_rename
                })
                
                if not success:
                    return f"error: {message}"
                
                print(f"[DEBUG] Результат операции с правами администратора: {message}")
                
                # Проверяем, была ли операция успешной
                if not os.path.exists(new_path):
                    return "error: Не удалось переименовать проект даже с правами администратора."
            
            # Обновляем текущий проект, если это он
            if self.current_project == oldProjectName:
                self.current_project = newProjectName
                print(f"[DEBUG] Текущий проект обновлен: {oldProjectName} -> {newProjectName}")
                
            # Если операция с правами администратора успешна, нам не нужно переименовывать файлы .rpp,
            # так как это уже сделано в скрипте администратора. Иначе обновляем имена файлов здесь:
            if os.path.exists(new_path) and not 'success' in locals():
                # Нужно также обновить имена файлов .rpp внутри папок сезонов и эпизодов
                for season_folder in [d for d in os.listdir(new_path) if os.path.isdir(os.path.join(new_path, d)) and d.startswith("S")]:
                    season_path = os.path.join(new_path, season_folder)
                    for episode_folder in [d for d in os.listdir(season_path) if os.path.isdir(os.path.join(season_path, d)) and d.startswith(season_folder + "-E")]:
                        reaper_path = os.path.join(season_path, episode_folder, "reaper")
                        if os.path.exists(reaper_path):
                            for file in os.listdir(reaper_path):
                                if file.endswith(".rpp") and file.startswith(oldProjectName):
                                    old_file_path = os.path.join(reaper_path, file)
                                    new_file_name = file.replace(oldProjectName, newProjectName, 1)
                                    new_file_path = os.path.join(reaper_path, new_file_name)
                                    try:
                                        os.rename(old_file_path, new_file_path)
                                        print(f"[DEBUG] Файл проекта переименован: {old_file_path} -> {new_file_path}")
                                    except Exception as e:
                                        print(f"[DEBUG] Ошибка при переименовании файла {old_file_path}: {str(e)}")
                                        # Продолжаем выполнение, так как эта ошибка не критична
            
            self.filesChanged.emit()  # Отправляем сигнал об изменении файлов
            return "success"
        except Exception as e:
            error_msg = f"error: {str(e)}"
            print(f"[DEBUG] Ошибка при переименовании проекта: {str(e)}")
            return error_msg

    def elevate_privileges(self, operation, args):
        """
        Запрашивает повышенные права админа для выполнения операции
        operation: строка с названием операции ('rename', 'delete', etc.)
        args: словарь с аргументами для операции
        """
        try:
            # Создаем временный файл для передачи параметров
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w', encoding='utf-8')
            temp_path = temp_file.name
            
            # Записываем данные операции в файл
            data = {
                'operation': operation,
                'args': args
            }
            json.dump(data, temp_file, ensure_ascii=False)
            temp_file.close()
            
            # Путь к текущему Python интерпретатору
            python_exe = sys.executable
            
            # Путь к вспомогательному скрипту (создадим его позже)
            helper_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'admin_helper.py')
            
            # Проверяем существование вспомогательного скрипта, если нет - создаем
            if not os.path.exists(helper_script):
                with open(helper_script, 'w', encoding='utf-8') as f:
                    f.write("""import os
import sys
import json
import shutil

def main():
    if len(sys.argv) != 2:
        print("Ошибка: Неверное количество аргументов")
        return 1
    
    temp_path = sys.argv[1]
    
    try:
        with open(temp_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        operation = data['operation']
        args = data['args']
        
        if operation == 'rename':
            old_path = args['old_path']
            new_path = args['new_path']
            
            if os.path.exists(old_path):
                os.rename(old_path, new_path)
                print(f"Успешно переименовано: {old_path} -> {new_path}")
                
                # Если нужно переименовать файлы внутри, тоже можно добавить здесь
                if 'files_to_rename' in args and args['files_to_rename']:
                    for old_file, new_file in args['files_to_rename']:
                        if os.path.exists(old_file):
                            os.rename(old_file, new_file)
                            print(f"Файл переименован: {old_file} -> {new_file}")
            else:
                print(f"Путь не существует: {old_path}")
                return 1
        
        # Можно добавить другие операции при необходимости
        
        # Удаляем временный файл
        os.remove(temp_path)
        return 0
    except Exception as e:
        print(f"Ошибка при выполнении операции: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
""")
            
            # Используем ShellExecute для запуска с правами администратора
            if ctypes.windll.shell32.IsUserAnAdmin():
                # Если уже есть права админа, просто запускаем скрипт
                result = subprocess.run([python_exe, helper_script, temp_path], capture_output=True, text=True)
                success = result.returncode == 0
                message = result.stdout.strip() if success else result.stderr.strip()
                
                # Удаляем временный файл
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                return success, message
            else:
                # Запрашиваем права администратора
                ctypes.windll.shell32.ShellExecuteW(
                    None,            # Дескриптор родительского окна
                    "runas",         # Операция (runas запрашивает права админа)
                    python_exe,      # Приложение
                    f'"{helper_script}" "{temp_path}"',  # Параметры
                    None,            # Рабочая директория
                    1                # Показать окно
                )
                
                # Возвращаем сообщение о том, что операция запущена с правами администратора
                return True, "Операция запущена с правами администратора."
        except Exception as e:
            print(f"[DEBUG] Ошибка при запросе прав администратора: {str(e)}")
            return False, f"Ошибка при запросе прав администратора: {str(e)}"