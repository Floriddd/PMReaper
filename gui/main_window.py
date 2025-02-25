import os
import requests
from packaging import version
from PyQt6.QtWidgets import QMainWindow, QSystemTrayIcon, QMenu, QApplication, QMessageBox
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWebChannel import QWebChannel
from gui.webengine import MyWebEngineView
from gui.update_dialog import UpdateDialog

GITHUB_API_URL = "https://api.github.com/repos/Floriddd/PMReaper/releases/latest"
__version__ = "1.2.1"

class MainWindow(QMainWindow):
    def __init__(self, bridge, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridge = bridge
        self.setWindowTitle("PMReaper (by FlorkA)")
        self.setFixedSize(1000, 700)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "ui", "favicon.ico")))

        self.channel = QWebChannel()
        self.channel.registerObject("pyBridge", self.bridge)

        dest_folder = os.path.join(os.getcwd(), "dropped_files")
        os.makedirs(dest_folder, exist_ok=True)

        self.view = MyWebEngineView(self.bridge, dest_folder, self)
        self.view.page().setWebChannel(self.channel)

        ui_path = os.path.join(os.path.dirname(__file__), "..", "ui", "index.html")
        url = QUrl.fromLocalFile(os.path.abspath(ui_path))
        self.view.load(url)

        self.setCentralWidget(self.view)
        self.init_tray_icon()
        self.show()
        self.check_for_updates(on_startup=True)

    def init_tray_icon(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "ui", "favicon.ico")))
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

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "PMReaper",
            "Приложение свернуто в трей.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def tray_icon_activated(self, reason):
        if reason in (QSystemTrayIcon.ActivationReason.Trigger, QSystemTrayIcon.ActivationReason.DoubleClick):
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
            download_url = assets[0].get("browser_download_url") if assets else None

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
        except Exception as e:
            QMessageBox.critical(self, "Ошибка обновления", f"Неизвестная ошибка при проверке обновлений: {e}")
