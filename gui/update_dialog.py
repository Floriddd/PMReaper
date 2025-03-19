import os
import webbrowser
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QProgressBar
from PyQt6.QtGui import QIcon, QFont, QDesktopServices
from PyQt6.QtCore import Qt, QUrl

class UpdateDialog(QDialog):
    def __init__(self, new_version, download_url, release_notes=None, parent=None):
        super().__init__(parent)
        self.new_version = new_version
        self.download_url = download_url
        self.release_notes = release_notes
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Доступно обновление")
        self.setFixedSize(500, 280)
        self.setWindowIcon(QIcon(os.path.join(os.path.dirname(__file__), "..", "ui", "favicon.svg")))
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 24, 24, 24)
        main_layout.setSpacing(16)

        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        
        title = QLabel(f"Доступна новая версия PMReaper!")
        title.setFont(title_font)
        main_layout.addWidget(title)

        version_layout = QHBoxLayout()
        
        version_info = QLabel(f"Версия <b>{self.new_version}</b> теперь доступна для установки.")
        version_info.setWordWrap(True)
        version_layout.addWidget(version_info, 1)
        
        icon_label = QLabel()
        icon_label.setPixmap(QIcon(os.path.join(os.path.dirname(__file__), "..", "ui", "favicon.svg")).pixmap(64, 64))
        version_layout.addWidget(icon_label)
        
        main_layout.addLayout(version_layout)

        separator = QLabel()
        separator.setFixedHeight(1)
        separator.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        main_layout.addWidget(separator)

        description = QLabel(
            "Рекомендуется обновить приложение до последней версии, чтобы получить все новые функции и исправления ошибок."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        main_layout.addWidget(description)

        whats_new_title = QLabel("Что нового:")
        whats_new_title.setStyleSheet("font-weight: bold;")
        main_layout.addWidget(whats_new_title)

        whats_new_text = self.release_notes if self.release_notes else "• Улучшенный интерфейс пользователя\n• Исправления ошибок\n• Улучшения производительности"
        whats_new = QLabel(whats_new_text)
        whats_new.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        whats_new.setWordWrap(True)
        main_layout.addWidget(whats_new)

        separator2 = QLabel()
        separator2.setFixedHeight(1)
        separator2.setStyleSheet("background-color: rgba(255, 255, 255, 0.1);")
        main_layout.addWidget(separator2)

        button_layout = QHBoxLayout()

        spacer = QLabel()
        button_layout.addWidget(spacer, 1)

        later_button = QPushButton("Позже")
        later_button.setFixedWidth(100)
        later_button.setCursor(Qt.CursorShape.PointingHandCursor)
        later_button.clicked.connect(self.close)
        button_layout.addWidget(later_button)

        download_button = QPushButton("Скачать")
        download_button.setFixedWidth(120)
        download_button.setCursor(Qt.CursorShape.PointingHandCursor)
        download_button.setStyleSheet("""
            QPushButton {
                background-color: #6e56cf;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #7c68d5;
            }
            QPushButton:pressed {
                background-color: #5d48b6;
            }
        """)
        download_button.clicked.connect(self.download_update)
        button_layout.addWidget(download_button)
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)

        self.setStyleSheet("""
            QDialog {
                background-color: #1e2028;
                color: #e2e8f0;
            }
            QLabel {
                color: #e2e8f0;
            }
            QPushButton {
                background-color: #262a35;
                color: #e2e8f0;
                border: 1px solid rgba(148, 163, 184, 0.15);
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                border-color: rgba(148, 163, 184, 0.3);
            }
            QPushButton:pressed {
                background-color: #1e2028;
            }
        """)
    
    def download_update(self):
        QDesktopServices.openUrl(QUrl(self.download_url))
        self.accept()
