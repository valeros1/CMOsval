echo "=== ТЕСТ 1: Тестовый режим с циклами ==="
python CMOsv.py -p "A" -v "1.0" -r "./test_repo.txt" -m -d 3

echo "=== ТЕСТ 2: Maven режим ==="
python CMOsv.py -p "junit:junit" -v "4.13.2" -r "https://repo1.maven.org/maven2" -d 2

echo "=== ТЕСТ 3: Ошибка - несуществующий пакет ==="
python CMOsv.py -p "com.nonexistent:fake" -v "1.0.0" -r "https://repo1.maven.org/maven2"

echo "=== ТЕСТ 4: Фильтр в тестовом режиме ==="
python CMOsv.py -p "A" -v "1.0" -r "./test_repo.txt" -m -f "B"

echo "=== ТЕСТ 5: BFS порядок обхода ==="
python CMOsv.py -p "A" -v "1.0" -r "./test_repo.txt" -m -d 2

