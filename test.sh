#!/bin/bash
#
#echo "=== ФИНАЛЬНЫЙ ТЕСТ (ВСЕ ИСПРАВЛЕНИЯ) ==="
#
#echo ""
#echo "1. Простой словарь (исправлено: test] -> test):"
#echo "([name:test])" | python3 CMOsv.py -o test1.xml
#echo "Результат:"
#cat test1.xml
#echo ""
#
#echo "2. Словарь с массивом:"
#echo "([numbers:'(1 2 3)])" | python3 CMOsv.py -o test2.xml
#echo "Результат:"
#cat test2.xml
#echo ""
#
#echo "3. С константой:"
#echo "set X=5;([value:|X|])" | python3 CMOsv.py -o test3.xml
#echo "Результат:"
#cat test3.xml
#echo ""
#
#echo "4. С вычислением:"
#echo "set A=10;set B=3;([sum:|A B +|])" | python3 CMOsv.py -o test4.xml
#echo "Результат:"
#cat test4.xml
#echo ""
#
#echo "5. С mod() (исправлено: 10 -> 1):"
#echo "set A=10;set B=3;([mod:|A B mod()|])" | python3 CMOsv.py -o test5.xml
#echo "Результат:"
#cat test5.xml
#echo ""
#
#echo "6. С concat():"
#echo "([concat:|hello world concat()|])" | python3 CMOsv.py -o test6.xml
#echo "Результат:"
#cat test6.xml
#
## Удаляем временные файлы
#echo ""
#echo "Очистка временных файлов..."
#rm -f test*.xml

#cat example1.cfg | python3 CMOsv.py -o example1.xml
#cat example2.cfg | python3 CMOsv.py -o example2.xml
#cat example3.cfg | python3 CMOsv.py -o example3.xml
cat example1.xml
cat example2.xml
cat example3.xml