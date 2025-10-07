import os
import socket
import argparse
import tomllib

def parse_arguments():
    """Парсим аргументы командной строки"""
    parser = argparse.ArgumentParser(
        description='Эмулятор командной оболочки ОС',
        epilog='Пример: python CMOsv.py --vfs ./my_vfs --script startup.txt --config config.toml'
    )

    parser.add_argument('--vfs', help='Путь к физическому расположению VFS')

    parser.add_argument('--script', help='Путь к стартовому скрипту')

    parser.add_argument('--config', help = 'Путь к конфигурационному файлу TOML')

    return parser.parse_args()


def load_config(config_path):
    """Загружаем конфигурацию из TOML файла"""
    if not config_path:
        print("Путь к конфигу не указан")
        return {}

    if not os.path.exists(config_path):
        print(f"Конфиг-файл не найден: {config_path}")
        return {}

    try:
        with open(config_path, 'rb') as f:
            # Читаем и парсим TOML файл
            config = tomllib.load(f)
        print(f"Конфиг загружен: {config_path}")
        return config
    except Exception as e:
        print(f"Ошибка чтения конфига {config_path}: {e}")
        return {}


def merge_configurations(args_config, file_config):
    """Логика приоритетов"""
    final_config = {}

    # Берем VFS путь (с приоритетом файла)
    if file_config.get('vfs_path'):
        final_config['vfs'] = file_config['vfs_path']
        print("VFS: использован путь из конфиг-файла")
    elif args_config.vfs:
        final_config['vfs'] = args_config.vfs
        print("VFS: использован путь из аргументов")
    else:
        final_config['vfs'] = None
        print("VFS: путь не указан")

    # Берем путь скрипта (с приоритетом файла)
    if file_config.get('script_path'):
        final_config['script'] = file_config['script_path']
        print("Скрипт: использован путь из конфиг-файла")
    elif args_config.script:
        final_config['script'] = args_config.script
        print("Скрипт: использован путь из аргументов")
    else:
        final_config['script'] = None
        print("Скрипт: путь не указан")

    return final_config


def script(script_path):
    """Выполнение стартового скрипта"""
    if not script_path:
        print("Путь к скрипту не указан")
        return True

    if not os.path.exists(script_path):
        print(f"Скрипт не найден: {script_path}")
        return False

    try:
        print(f"Выполняем скрипт: {script_path}")
        with open(script_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, 1):
            line = line.strip()

            # Пропускаем пустые строки
            if not line:
                continue

            print(line)

            parts = line.split()
            cmd = parts[0]
            args = parts[1:]

            if cmd not in ['ls', 'cd', 'exit']:
                print(f"Ошибка в строке {line_num}: команда '{cmd}' не найдена")
                return False  # Останавливаемся при первой ошибке

            else:
                print(cmd, args)



        print("Скрипт выполнен успешно")
        return True

    except Exception as e:
        print(f"Ошибка выполнения скрипта {script_path}: {e}")
        return False


def get_username():
    """Функция для получения имени текущего пользователя."""
    return os.getlogin()

def get_hostname():
    """Функция для получения имени компьютера (хоста)."""
    return socket.gethostname()

def main():

    args = parse_arguments()

    file_config = {}
    if args.config:
        file_config = load_config(args.config)

    final_config = merge_configurations(args, file_config)



    if final_config['script']:
        script_success = script(final_config['script'])
        if not script_success:
            print("Ошибка в скрипте")
            return
        print("------------------------------------------")

    print("------------------------------------------")
    print("Из командной строки:")
    print(f"  VFS: {args.vfs}")
    print(f"  Скрипт: {args.script}")
    print(f"  Конфиг: {args.config}")
    print('-' * 25)
    print("Из конфиг-файла:")
    print(f"  VFS: {file_config.get('vfs_path', 'Не указан')}")
    print(f"  Скрипт: {file_config.get('script_path', 'Не указан')}")
    print('-' * 25)
    print("Итоговый результат:")
    print(f"  VFS: {final_config['vfs']}")
    print(f"  Скрипт: {final_config['script']}")
    print("------------------------------------------")
    print("Для выхода введите команду 'exit'.")
    print("Доступные команды: ls, cd, exit")

    while True:
        username = get_username()
        hostname = get_hostname()
        prompt = f"{username}@{hostname}:~$ "
        user_input = input(prompt).strip()
        parts = user_input.split()

        if not parts:
            continue

        cmd = parts[0]
        args = parts[1:]

        match cmd:
            case "ls":
                print(cmd, args)

            case "cd":
                print(cmd, args)

            case "exit":
                print("Выход из эмулятора. До свидания!")
                break

            case _:
                print(f"Команда '{cmd}' не найдена. Доступные команды: ls, cd, exit")

if __name__ == "__main__":
    main()












