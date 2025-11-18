# Тест 4: Несуществующий пакет
python CMOsv.py -p "com.nonexistent:fake" -v "1.0.0" -r "https://repo1.maven.org/maven2"
echo "---------------------------------------------------------------------------"

# Тест 5: Неправильный формат пакета
python CMOsv.py -p "invalid-format" -v "1.0.0" -r "https://repo1.maven.org/maven2"
echo "---------------------------------------------------------------------------"

# Тест 6: Несуществующая версия
python CMOsv.py -p "com.google.guava:guava" -v "999.999.999" -r "https://repo1.maven.org/maven2"