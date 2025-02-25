import os
import sys
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QSharedMemory
from bridge.bridge import Bridge
from gui.main_window import MainWindow

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