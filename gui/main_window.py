import os
import requests
import json
from packaging import version
from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QApplication, QMessageBox, QFileDialog
from PyQt6.QtCore import QUrl, Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWebChannel import QWebChannel
from gui.webengine import MyWebEngineView
from gui.update_dialog import UpdateDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView

GITHUB_API_URL = "https://api.github.com/repos/Floriddd/PMReaper/releases/latest"
__version__ = "1.4.0"

class MainWindow(QMainWindow):
    def __init__(self, bridge, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridge = bridge
        self.setWindowTitle("PMReaper")
        self.setFixedSize(1000, 800)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "ui", "favicon.svg")))

        self.channel = QWebChannel()
        self.channel.registerObject("pyBridge", self.bridge)

        dest_folder = os.path.join(os.getcwd(), "dropped_files")
        os.makedirs(dest_folder, exist_ok=True)

        self.view = MyWebEngineView(self.bridge, dest_folder, self)
        self.view.page().setWebChannel(self.channel)

        self.setup_bridge_extensions()

        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "index.html")
        url = QUrl.fromLocalFile(os.path.abspath(ui_path))
        self.view.load(url)

        self.setCentralWidget(self.view)
        self.init_tray_icon()
        self.show()

        self.check_for_updates(on_startup=True)

        self.bridge.filesChanged.connect(self.updateFiles)

        self.devtools = QWebEngineView()
        self.view.page().setDevToolsPage(self.devtools.page())

    def setup_bridge_extensions(self):
        """Добавляет дополнительные методы для моста Python-JavaScript"""
        setattr(self.bridge, 'browseReaperPath', self.browse_reaper_path)
        setattr(self.bridge, 'openProjectFolder', self.open_project_folder)
        setattr(self.bridge, 'getSystemInfo', self.get_system_info)
        setattr(self.bridge, 'getCurrentProject', self.bridge.getCurrentProject)
        setattr(self.bridge, 'getBaseDir', self.bridge.getBaseDir)

    @pyqtSlot(result=str)
    def get_system_info(self):
        """Возвращает информацию о системе в формате JSON"""
        info = {
            "os": os.name,
            "version": __version__,
            "pythonVersion": ".".join(map(str, os.sys.version_info[:3])),
            "qtVersion": "PyQt6"
        }
        return json.dumps(info)
        
    @pyqtSlot(result=str)
    def browse_reaper_path(self, callback):
        """Открывает диалог выбора пути к Reaper и вызывает callback с результатом"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выбрать исполняемый файл Reaper",
            "",
            "Исполняемые файлы (*.exe);;Все файлы (*)"
        )
        
        if file_path:
            self.view.page().runJavaScript(f"{callback}('{file_path.replace('\\', '\\\\')}')")
            return file_path
        return ""
        
    @pyqtSlot(str)
    def open_project_folder(self, folder_path=None):
        """Открывает папку проекта в проводнике"""
        if folder_path and os.path.exists(folder_path):
            path = folder_path
        else:
            self.view.page().runJavaScript(
                "getCurrentProjectPath()",
                lambda path: self._open_folder(path) if path else None
            )
            return
            
        self._open_folder(path)
            
    def _open_folder(self, path):
        """Вспомогательный метод для открытия папки"""
        if path and os.path.exists(path):
            os.startfile(path)
        else:
            self.show_status_message("Папка проекта не найдена")

    def keyPressEvent(self, event):
        """Обработка горячих клавиш"""
        if event.key() == Qt.Key.Key_F12:
            self.devtools.show()
        elif event.key() == Qt.Key.Key_F5:
            self.view.reload()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:
            self.view.reload()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_I:
            self.devtools.show()
        elif event.modifiers() & Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Q:
            QApplication.instance().quit()
        else:
            super().keyPressEvent(event)

    def init_tray_icon(self):
        """Инициализация иконки в трее"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "ui", "favicon.svg")))
        self.tray_icon.activated.connect(self.tray_icon_activated)

        tray_menu = QMenu()

        open_action = QAction("Открыть", self)
        open_action.triggered.connect(self.show_window_from_tray)
        tray_menu.addAction(open_action)
        
        check_update_action = QAction("Проверить обновления", self)
        check_update_action.triggered.connect(self.check_for_updates)
        tray_menu.addAction(check_update_action)
        
        tray_menu.addSeparator()

        version_label = QAction(f"Версия: {__version__}", self)
        version_label.setEnabled(False)
        tray_menu.addAction(version_label)
        
        tray_menu.addSeparator()

        close_action = QAction("Выход", self)
        close_action.triggered.connect(QApplication.instance().quit)
        tray_menu.addAction(close_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        self.tray_icon.setToolTip("PMReaper")

    def closeEvent(self, event):
        """Обработка события закрытия окна"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "PMReaper",
            "Приложение свернуто в трей.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def tray_icon_activated(self, reason):
        """Обработка активации иконки в трее"""
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
            self.show_window_from_tray()

    def show_window_from_tray(self):
        """Показывает окно из трея"""
        self.showNormal()
        self.activateWindow()
        self.raise_()

    def raise_(self):
        """Поднимает окно на передний план"""
        self.setWindowState(self.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)
        self.activateWindow()
        
    def show_status_message(self, message, duration=3000):
        """Показывает сообщение в UI через JavaScript"""
        js = f"showToast('{message}', 'info', {duration})"
        self.view.page().runJavaScript(js)

    def check_for_updates(self, on_startup=False):
        """Проверка наличия обновлений"""
        try:
            response = requests.get(GITHUB_API_URL)
            response.raise_for_status()
            release_info = response.json()
            latest_version_tag = release_info.get("tag_name")
            latest_version = latest_version_tag.lstrip('v') if latest_version_tag else None

            assets = release_info.get("assets", [])
            download_url = assets[0].get("browser_download_url") if assets else None
            release_notes = release_info.get("body", "")  # Получаем описание релиза

            if latest_version and download_url:
                current_version = __version__
                if version.parse(latest_version) > version.parse(current_version):
                    dialog = UpdateDialog(latest_version, download_url, release_notes, self)
                    dialog.exec()
                else:
                    if not on_startup:
                        self.show_status_message("У вас установлена последняя версия.")
            else:
                if not on_startup:
                    self.show_status_message("Не удалось получить информацию о последней версии.", 5000)
        except requests.exceptions.RequestException as e:
            if not on_startup:
                self.show_status_message(f"Ошибка при проверке обновлений: {e}", 5000)
        except Exception as e:
            if not on_startup:
                self.show_status_message(f"Неизвестная ошибка при проверке обновлений: {e}", 5000)

    def updateFiles(self):
        """Обновляет список файлов в UI"""
        self.view.page().runJavaScript("updateRightPanel(currentSeason, currentEpisode);")
