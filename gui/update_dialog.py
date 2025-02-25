import webbrowser
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QMessageBox

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
