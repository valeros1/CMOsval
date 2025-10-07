echo "1. Запуск без параметров:"
python CMOsv.py

echo ""

echo "1. Тест --vfs:"
python CMOsv.py --vfs ./test_vfs

echo ""

echo "2. Тест --script:"
python CMOsv.py --script script.txt