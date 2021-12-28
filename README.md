# Dnavplot

This is a toolset for plotting graphs from log data in Python.
For now is supported **.dat** and **.csv** data formats.

# Requariments

```
numpy
matplotlib
```

# Usage
For import csv data format:
```
./dnavimport_csv.py -i examples/data.csv
```

For plotting graphs
```
./dnavplot.py -f tmp/Veast.dat tmp/Vup.dat tmp/Vdown.dat -c 2 1 
```

You can use 'x' and 'z' buttuns to zoom and undo. Also 't' buttun make markers on line, 'q' for quit. 
