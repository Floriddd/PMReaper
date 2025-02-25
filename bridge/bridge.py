import os
import json
import shutil
import appdirs
import webbrowser
from PyQt6.QtCore import pyqtSlot, QObject
from PyQt6.QtWidgets import QFileDialog, QMessageBox

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

    @pyqtSlot(str, result=str)
    def setBaseDirectory(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.base_directories = [path]
            self.current_base_directory_index = 0
            self.saveConfig()
            return "Базовая директория установлена успешно."
        else:
            return "Неверный путь. Папка не существует."

    @pyqtSlot(result=str)
    def browseDirectory(self):
        print("Python: browseDirectory вызвана")
        directory = QFileDialog.getExistingDirectory(None, "Выберите папку для проектов", os.path.expanduser("~"))
        if directory:
            return directory
        else:
            return ""

    @pyqtSlot(str, result=str)
    def addBaseDirectory(self, path):
        print(f"Python: addBaseDirectory вызвана с путем: {path}")
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
                self.current_base_directory_index = max(0, len(self.base_directories) - 1)
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
            return json.dumps(self.base_directories)
        except Exception as e:
            print("Ошибка при формировании списка базовых директорий:", e)
            return json.dumps([])

    @pyqtSlot(result=str)
    def listProjects(self):
        print("Python: listProjects вызвана")
        if not self.base_dir or not os.path.isdir(self.base_dir):
            print("Базовая директория не установлена или не существует.")
            return json.dumps([])
        try:
            projects = [d for d in os.listdir(self.base_dir) if os.path.isdir(os.path.join(self.base_dir, d))]
            print("Найденные проекты:", projects)
            return json.dumps(projects)
        except Exception as e:
            print(f"Ошибка в listProjects: {e}")
            return json.dumps([])

    @pyqtSlot(str, result=str)
    def createProject(self, projectName):
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
            print(f"Ошибка в listEpisodes: {e}")
            return json.dumps({})

    @pyqtSlot(str, int, result=str)
    def addSeason(self, projectName, season):
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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

    @pyqtSlot(str, int, int, int, result=str)
    def renameSeason(self, projectName, oldSeason, newSeason):
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        if not self.base_dir or not os.path.isdir(self.base_dir):
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
        except ValueError:
            print("[DEBUG] Ошибка: Season или episode не является числом")