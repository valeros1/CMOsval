python CMOsv.py -p "Newtonsoft.Json" -r "https://api.nuget.org/v3/index.json"
python CMOsv.py -p "MyPackage" -r "/path/to/repo.txt" -m -v "1.0.0" -o "graph.svg" -a -d 5 -f "test"
python CMOsv.py -p "test-package" -r "repo.json"