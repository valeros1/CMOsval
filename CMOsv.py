import argparse
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import deque


class DependencyNode:
    """Узел графа зависимостей"""

    def __init__(self, package_name, version):
        self.package_name = package_name
        self.version = version
        self.dependencies = []  # прямые зависимости
        self.level = 0  # уровень в графе

    def __str__(self):
        return f"{self.package_name}:{self.version}"

    def __eq__(self, other):
        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))


def build_dependency_graph_bfs(start_package, start_version, repo_url, max_depth=10, filter_str="", test_mode=False):
    """
    Построение графа зависимостей с помощью BFS с рекурсией
    """
    visited = set()

    # Создаём корневой узел
    root_node = DependencyNode(start_package, start_version)
    root_node.level = 0
    visited.add(str(root_node))

    def bfs_recursive(current_level_nodes, current_depth):
        """
        current_level_nodes - узлы текущего уровня
        current_depth - текущая глубина
        """
        # Базовый случай рекурсии
        if not current_level_nodes or current_depth >= max_depth:
            return

        next_level_nodes = []

        # Обрабатываем все узлы текущего уровня
        for current_node in current_level_nodes:
            print(f"Обрабатываем {current_node} (уровень {current_depth})")

            try:
                # Получаем прямые зависимости для текущего узла
                dependencies = get_dependencies(current_node.package_name, current_node.version, repo_url, test_mode)

                # Обрабатываем каждую зависимость
                for dep in dependencies:
                    if ':' in dep:
                        parts = dep.split(':')

                        if test_mode:
                            dep_package = parts[0]
                            dep_version = parts[1] if len(parts) > 1 else "1.0"
                        else:
                            dep_package = f"{parts[0]}:{parts[1]}"
                            dep_version = parts[2] if len(parts) > 2 else "unknown"

                        # Проверяем фильтр
                        if filter_str and filter_str in dep_package:
                            print(f"Пропущен по фильтру '{filter_str}': {dep_package}:{dep_version}")
                            continue

                        # Создаём узел для зависимости
                        dep_node = DependencyNode(dep_package, dep_version)
                        dep_node.level = current_depth + 1

                        # Проверяем циклические зависимости
                        if str(dep_node) in visited:
                            print(f"Обнаружена циклическая зависимость: {dep_node}")
                            current_node.dependencies.append(dep_node)
                            continue

                        # Добавляем в посещённые и в следующий уровень
                        visited.add(str(dep_node))
                        current_node.dependencies.append(dep_node)
                        next_level_nodes.append(dep_node)

            except Exception as e:
                print(f"Ошибка при обработке {current_node}: {e}")

        # Рекурсивный вызов для СЛЕДУЮЩЕГО уровня с УВЕЛИЧЕННОЙ глубиной
        bfs_recursive(next_level_nodes, current_depth + 1)

    # Запускаем BFS с корневым узлом и глубиной 0
    bfs_recursive([root_node], 0)
    return root_node


def print_dependency_graph(node, indent=0):
    """Красивый вывод графа зависимостей"""
    prefix = "  " * indent + "├── " if indent > 0 else ""
    print(f"{prefix}{node.package_name}:{node.version}")

    for dep in node.dependencies:
        print_dependency_graph(dep, indent + 1)


def get_test_dependencies(package_name, repo_url):
    """
    Получить зависимости из тестового файла
    Формат файла: A: B, C, D
    """
    try:
        with open(repo_url, 'r', encoding='utf-8') as f:
            content = f.read()

        # Извлекаем только имя пакета (без версии)
        search_name = package_name.split(':')[0] if ':' in package_name else package_name

        for line in content.split('\n'):
            line = line.strip()
            if ':' in line:
                current_package, deps_part = line.split(':', 1)
                current_package = current_package.strip()

                if current_package == search_name:
                    dependencies = [dep.strip() for dep in deps_part.split(',') if dep.strip()]
                    print(f"Найдены зависимости для {search_name}: {dependencies}")
                    return dependencies

        print(f"Пакет {search_name} не найден в файле")
        return []

    except Exception as e:
        print(f"Ошибка чтения тестового файла: {e}")
        return []


def get_dependencies(package_name, version, repo_url, test_mode=False):
    """
    Универсальная функция получения зависимостей
    Поддерживает как Maven, так и тестовый режим
    """
    if test_mode:
        # Тестовый режим - используем файл
        print(f"Тестовый режим: ищем зависимости для {package_name} в файле {repo_url}")
        dependencies = get_test_dependencies(package_name, repo_url)
        # Преобразуем в формат "пакет:версия"
        return [f"{dep}:1.0" for dep in dependencies if dep]  # убираем пустые
    else:
        # Режим Maven - используем старую функцию
        print(f"Maven режим: ищем зависимости для {package_name}:{version}")
        return get_maven_dependencies(package_name, version, repo_url)


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
        help="Режим работы с тестового репозитория"
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

    # Выводим зависимости
    if dependencies:
        print(f"\nПрямые зависимости {args.package_name}:{args.version}:")
        for i, dep in enumerate(dependencies, 1):
            print(f"  {i}. {dep}")
    else:
        print(f"\nЗависимости не найдены для {args.package_name}")

    print("\n" + "-" * 50)
    print("ЭТАП 3: ПОСТРОЕНИЕ ПОЛНОГО ГРАФА ЗАВИСИМОСТЕЙ")
    print("-" * 50)

    print(f"Параметры анализа:")
    print(f"  - Максимальная глубина: {args.max_depth}")
    print(f"  - Фильтр пакетов: '{args.filter}'")
    print(f"  - Режим тестирования: {args.repo_mode}")

    # Строим полный граф с помощью BFS
    root_node = build_dependency_graph_bfs(
        start_package=args.package_name,
        start_version=args.version,
        repo_url=args.repo_url,
        max_depth=args.max_depth,
        filter_str=args.filter,
        test_mode=args.repo_mode
    )

    # Выводим граф
    print(f"\nПолный граф зависимостей {args.package_name}:{args.version}:")
    print_dependency_graph(root_node)


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


if __name__ == "__main__":
    command_line()