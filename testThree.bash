echo "1. Все параметры вместе:"
python CMOsv.py --vfs ./test_vfs --script script.txt --config config.toml

echo ""

echo "2. Комбинация VFS + конфиг:"
python CMOsv.py --vfs ./test_vfs --config config.toml

echo ""

echo "3. Комбинация скрипт + конфиг:"
python CMOsv.py --script script.txt --config config.toml