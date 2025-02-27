import os
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt
from PyQt6.QtWebEngineCore import QWebEngineSettings
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragMoveEvent
from utils.file_ops import copy_file

class MyWebEngineView(QWebEngineView):
    def __init__(self, bridge, dest_folder, main_window, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bridge = bridge
        self.dest_folder = dest_folder
        self.main_window = main_window
        self.setAcceptDrops(True)
        self.setAttribute(Qt.WidgetAttribute.WA_AcceptDrops, True)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.page().settings().setAttribute(QWebEngineSettings.WebAttribute(13), True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            print("[DEBUG] dragEnterEvent: принимаем событие")
        else:
            event.ignore()

    def dragMoveEvent(self, event: QDragMoveEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        print("[DEBUG] Python: dropEvent: событие drop получено")
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
                        print("[DEBUG] Проект, сезон или эпизод не выбраны, или базовая директория не установлена.")
                        return

                    project_path = os.path.join(base_dir, project_name)
                    season_folder = f"S{int(season):02d}"
                    episode_folder = f"{season_folder}-E{int(episode):02d}"
                    target_folder_map = {"raws": "raws", "roads": "outs", "voice": "source", "subs": "subs"}
                    target_folder_name = target_folder_map.get(target_folder_type)

                    if not target_folder_name:
                        print("[DEBUG] Неверный тип папки:", target_folder_type)
                        return

                    for file_path in files:
                        filename = os.path.basename(file_path)
                        dest_path = os.path.join(project_path, target_folder_name, season_folder, episode_folder, filename)
                        copy_file(file_path, dest_path)
                else:
                    print("[DEBUG] Неверная зона для Drop")

            self.page().runJavaScript(get_folder_type_js, handle_js_result)
        else:
            print("[DEBUG] В dropEvent нет URL")
