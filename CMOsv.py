import os
import socket

def get_username():
    """Функция для получения имени текущего пользователя."""
    return os.getlogin()

def get_hostname():
    """Функция для получения имени компьютера (хоста)."""
    return socket.gethostname()

def main():

    print("Добро пожаловать в эмулятор командной оболочки!")
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

