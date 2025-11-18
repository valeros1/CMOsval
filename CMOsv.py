import argparse
import sys
import urllib.request
import xml.etree.ElementTree as ET


def get_maven_dependencies(package_name, version, repo_url):

    try:
        # Разделяем group:artifact
        group_id, artifact_id = package_name.split(':')

        # Формируем URL к POM-файлу
        group_path = group_id.replace('.', '/')
        repo_url = repo_url.rstrip('/')
        pom_url = f"{repo_url}/{group_path}/{artifact_id}/{version}/{artifact_id}-{version}.pom"

        print(f"Загружаем: {pom_url}")

        # Скачиваем POM
        with urllib.request.urlopen(pom_url) as response:
            pom_content = response.read()

        # Парсим XML
        root = ET.fromstring(pom_content)

        # Ищем зависимости
        dependencies = []
        for dep in root.findall('.//{http://maven.apache.org/POM/4.0.0}dependency'):
            group_elem = dep.find('{http://maven.apache.org/POM/4.0.0}groupId')
            artifact_elem = dep.find('{http://maven.apache.org/POM/4.0.0}artifactId')
            version_elem = dep.find('{http://maven.apache.org/POM/4.0.0}version')

            if group_elem is not None and artifact_elem is not None:
                dep_name = f"{group_elem.text}:{artifact_elem.text}"
                if version_elem is not None:
                    dep_name += f":{version_elem.text}"
                dependencies.append(dep_name)

        return dependencies

    except Exception as e:
        print(f"Ошибка при получении зависимостей: {e}")
        return []


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

    print("ЭТАП 2: ПОЛУЧЕНИЕ ЗАВИСИМОСТЕЙ MAVEN")
    print("=" * 50)

    # Получаем зависимости
    dependencies = get_maven_dependencies(
        args.package_name,
        args.version,
        args.repo_url
    )

    # Выводим зависимости (Пункт 4)
    if dependencies:
        print(f"\nПрямые зависимости {args.package_name}:{args.version}:")
        for i, dep in enumerate(dependencies, 1):
            print(f"  {i}. {dep}")
    else:
        print(f"\nЗависимости не найдены для {args.package_name}")

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