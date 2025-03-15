import os
import json


def get_directory_structure(root_dir):
    """
    Обходить файлову систему і повертає структуру директорій у вигляді словника.
    """
    structure = {}
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Відносний шлях директорії
        relative_path = os.path.relpath(dirpath, root_dir)
        # Пропускаємо поточний рівень, якщо це root
        if relative_path == ".":
            relative_path = ""
        # Додаємо список піддиректорій і файлів
        structure[relative_path] = {
            "directories": dirnames,
            "files": filenames,
        }
    return structure


def save_structure_to_json(structure, output_file):
    """
    Зберігає структуру у форматі JSON.
    """
    with open(output_file, "w", encoding="utf-8") as json_file:
        json.dump(structure, json_file, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    # Вкажіть кореневу директорію проєкту
    project_root = input("Введіть шлях до кореневої директорії вашого проєкту: ").strip()
    output_file = "project_structure.json"

    if os.path.exists(project_root) and os.path.isdir(project_root):
        # Отримуємо структуру проєкту
        structure = get_directory_structure(project_root)
        # Зберігаємо в JSON
        save_structure_to_json(structure, output_file)
        print(f"Структуру проєкту збережено у файл {output_file}")
    else:
        print("Вказаний шлях не існує або це не директорія.")
