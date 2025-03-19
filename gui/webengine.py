import os
import sys
import shutil
from PyQt6.QtCore import QUrl, QObject, pyqtSlot, Qt
from PyQt6.QtWidgets import QFileDialog
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

class CustomWebEnginePage(QWebEnginePage):
    """Расширенная веб-страница с улучшенной поддержкой навигации и перехватом ошибок"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.featurePermissionRequested.connect(self.onFeaturePermissionRequested)
        
    def javaScriptConsoleMessage(self, level, message, line, source):
        """Логирование JavaScript-сообщений"""
        log_levels = {
            QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "INFO",
            QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "WARNING",
            QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "ERROR"
        }
        level_str = log_levels.get(level, "UNKNOWN")
        if level == QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel:
            print(f"JS {level_str}: {message} [line {line}] in {source}")
    
    def acceptNavigationRequest(self, url, nav_type, is_main_frame):
        """Обработка запросов навигации"""
        if nav_type == QWebEnginePage.NavigationType.NavigationTypeLinkClicked:
            if url.scheme() in ['http', 'https']:
                import webbrowser
                webbrowser.open(url.toString())
                return False
        return super().acceptNavigationRequest(url, nav_type, is_main_frame)
        
    def onFeaturePermissionRequested(self, url, feature):
        """Обработка запросов разрешений функций"""
        self.setFeaturePermission(url, feature, QWebEnginePage.PermissionPolicy.PermissionGrantedByUser)

class MyWebEngineView(QWebEngineView):
    """Расширенный веб-движок с поддержкой перетаскивания файлов и дополнительными возможностями"""
    
    def __init__(self, bridge, dest_folder, parent=None):
        super().__init__(parent)
        self.bridge = bridge
        self.dest_folder = dest_folder
        self.setAcceptDrops(True)

        self.setPage(CustomWebEnginePage(self))

        self.page().settings().setAttribute(self.page().settings().WebAttribute.JavascriptEnabled, True)
        self.page().settings().setAttribute(self.page().settings().WebAttribute.LocalContentCanAccessFileUrls, True)
        self.page().settings().setAttribute(self.page().settings().WebAttribute.LocalContentCanAccessRemoteUrls, True)
        self.page().settings().setAttribute(self.page().settings().WebAttribute.LocalStorageEnabled, True)

        if hasattr(sys, "_MEIPASS") is False:
            try:
                self.page().settings().setAttribute(self.page().settings().WebAttribute.DeveloperExtrasEnabled, True)
            except AttributeError:
                try:
                    self.page().settings().setAttribute(self.page().settings().WebAttribute.WebDeveloperExtras, True)
                except AttributeError:
                    print("Предупреждение: Не удалось включить инструменты разработчика. Атрибут не найден в WebAttribute.")

    def dragEnterEvent(self, event: QDragEnterEvent):
        """Обработка начала перетаскивания файлов"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.page().runJavaScript("if (window.dragEnterUI) window.dragEnterUI();")
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """Обработка выхода перетаскивания за границы"""
        self.page().runJavaScript("if (window.dragLeaveUI) window.dragLeaveUI();")
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent):
        """Обработка события сброса файлов"""
        event.acceptProposedAction()
        urls = event.mimeData().urls()

        position = event.position()
        js_code = """
        (function() {
            try {
                const element = document.elementFromPoint(%d, %d);
                if (!element) return null;
                
                if (element.classList.contains('file-list')) {
                    return element.id;
                }
                
                const fileList = element.closest('.file-list');
                if (fileList) {
                    return fileList.id;
                }
                
                const allFileLists = document.querySelectorAll('.file-list');
                for (const list of allFileLists) {
                    const rect = list.getBoundingClientRect();
                    if (
                        rect.left <= %d && 
                        rect.right >= %d && 
                        rect.top <= %d && 
                        rect.bottom >= %d
                    ) {
                        return list.id;
                    }
                }
                
                return null;
            } catch (err) {
                console.error('Ошибка при определении целевого элемента:', err);
                return null;
            }
        })();
        """ % (position.x(), position.y(), position.x(), position.x(), position.y(), position.y())
        
        self.page().runJavaScript(js_code, lambda result: self._processDropWithTargetId(urls, result))

        self.page().runJavaScript("if (window.dragLeaveUI) window.dragLeaveUI();")
    
    def _processDropWithTargetId(self, urls, element_id):
        """Обрабатывает перетаскивание файлов с определенным ID элемента"""
        print(f"[DEBUG] Получен ID элемента для сброса: {element_id}")

        if not element_id:
            self.page().runJavaScript(
                "window.currentDropTarget || null;",
                lambda target_type: self._processDroppedFiles(urls, target_type)
            )
            return

        target_type_map = {
            'rawsList': 'raws',
            'roadsList': 'roads',
            'voiceList': 'voice',
            'subsList': 'subs'
        }
        
        target_type = target_type_map.get(element_id)
        print(f"[DEBUG] Определен тип цели: {target_type} для элемента {element_id}")

        self._processDroppedFiles(urls, target_type)

    def _processDroppedFiles(self, urls, target_type):
        """Обрабатывает сброшенные файлы после получения целевого типа"""
        print(f"[DEBUG] Обработка файлов для цели: {target_type}")
        
        if not target_type:
            print("[ОШИБКА] Не удалось определить целевой блок для перетаскивания")
            self.page().runJavaScript(
                "showToast('Ошибка: Не удалось определить целевой блок. Попробуйте точнее перетащить файл на нужный блок.', 'error', 5000);"
            )
            return

        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                dest_file_path = os.path.join(self.dest_folder, os.path.basename(file_path))
                print(f"[DEBUG] Копирование файла: {file_path} -> {dest_file_path}")
                try:
                    shutil.copy2(file_path, dest_file_path)
                except Exception as e:
                    print(f"[ОШИБКА] Не удалось скопировать файл: {e}")
                    self.page().runJavaScript(
                        f"showToast('Ошибка копирования файла: {str(e)}', 'error', 3000);"
                    )
                    continue

                print(f"[DEBUG] Вызов bridge.dragDropFile с {dest_file_path} -> {target_type}")
                self.bridge.dragDropFile(dest_file_path, target_type)

                folder_names = {
                    'raws': 'Равки',
                    'roads': 'Делённые дороги', 
                    'voice': 'Озвучка',
                    'subs': 'Субтитры'
                }
                folder_name = folder_names.get(target_type, target_type)
                self.page().runJavaScript(
                    f"showToast('Файл добавлен в «{folder_name}»', 'success');"
                )

    def contextMenuEvent(self, event):
        """Настраиваем контекстное меню"""
        if hasattr(sys, "_MEIPASS"):
            return

        super().contextMenuEvent(event)
