import argparse
import sys


def command_line():
    """
    Минимальное CLI-приложение для визуализации графа зависимостей
    Вариант №17, Этап 1
    """
    parser = argparse.ArgumentParser(
        description='Инструмент визуализации графа зависимостей для менеджера пакетов'
    )

    # Имя анализируемого пакета (обязательный)
    parser.add_argument(
        "-p", "--package-name",
        type=str,
        required=True,
        help="Имя анализируемого пакета"
    )

    # URL-адрес репозитория или путь к файлу тестового репозитория (обязательный)
    parser.add_argument(
        "-r", "--repo-url",
        type=str,
        required=True,
        help="URL-адрес репозитория или путь к файлу тестового репозитория"
    )

    # Режим работы с тестовым репозиторием
    parser.add_argument(
        "-m", "--repo-mode",
        action="store_true",
        help="Режим работы с тестовым репозиторием"
    )

    # Версия пакета
    parser.add_argument(
        "-v", "--version",
        type=str,
        default="latest",
        help="Версия пакета"
    )

    # Имя сгенерированного файла с изображением графа
    parser.add_argument(
        "-o", "--output-image",
        type=str,
        default="dependency_graph.png",
        help="Имя сгенерированного файла с изображением графа"
    )

    # Режим вывода зависимостей в формате ASCII-дерева
    parser.add_argument(
        "-a", "--ascii-tree",
        action="store_true",
        help="Режим вывода зависимостей в формате ASCII-дерева"
    )

    # Максимальная глубина анализа зависимостей
    parser.add_argument(
        "-d", "--max-depth",
        type=int,
        default=10,
        help="Максимальная глубина анализа зависимостей"
    )

    # Подстрока для фильтрации пакетов
    parser.add_argument(
        "-f", "--filter",
        type=str,
        default="",
        help="Подстрока для фильтрации пакетов"
    )

    # Парсинг аргументов
    args = parser.parse_args()

    errors = validate_arguments(args)
    if errors:
        print("Обнаружены ошибки в параметрах:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)

    args_dict = vars(args)

    print(50 * "=")
    for key, value in args_dict.items():
        print(f"{key}: {value}")

def validate_arguments(args):

    errors = []

        # Проверка обязательных параметров
    if not args.package_name or not args.package_name.strip():
        errors.append("имя пакета не может быть пустым")

    if not args.repo_url or not args.repo_url.strip():
        errors.append("источник не может быть пустым")

        # Проверка максимальной глубины
    if args.max_depth <= 0:
        errors.append("максимальная глубина должна быть положительным числом")

        # Проверка версии (если указана)
    if args.version and args.version != "latest":
        if not args.version[0].isdigit():
            errors.append("версия должна начинаться с цифры")

        # Простая проверка выходного файла
    if args.output_image and not args.output_image.endswith(('.png', '.jpg', '.jpeg', '.svg')):
        errors.append("выходной файл должен быть изображением (.png, .jpg, .jpeg, .svg)")

    return errors

command_line()