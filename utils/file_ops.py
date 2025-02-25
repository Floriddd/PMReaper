import shutil

def copy_file(src, dest):
    try:
        shutil.copy2(src, dest)
        print(f"Файл {src} скопирован в {dest}")
    except Exception as e:
        print(f"Ошибка при копировании файла {src}: {e}")

def move_file(src, dest):
    try:
        shutil.move(src, dest)
        print(f"Файл перемещён из {src} в {dest}")
    except Exception as e:
        print(f"Ошибка при перемещении файла: {e}")
