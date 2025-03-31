import os
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
