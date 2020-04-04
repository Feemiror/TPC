
# TPC - Titanic passengers data comparison library
TPC is a Python library used to compare expected and actual versions of famous Titanic passengers dataset.
With a little effort it can be converted to any database comparison tool.

# Installation
Project is created with Python >= 3.6
To run this library locally, consider setting up a virtual environment using [venv](https://docs.python.org/3/library/venv.html):

```
 $ python venv venv
 $ venv\Scriptis\activate.bat
 $ (venv) python --install -r requirements.txt
```

# Usage

## From command line

Recommended way of running script is from command line with arguments:

```
$ (venv) python TPC.py -h

    usage: TPC.py [-h] -i INPUTFILE -o OUTPUTFILE [-e EXCEL] [-c COLUMNS]
                  [-p PASSENGERID] [-v] [-f]

    optional arguments:
      -h, --help            show this help message and exit
      -i, --inputfile       path to CSV or JSON input file
      -o, --outputfile      path to CSV or TXT output file
      -e, --excel           path to XLS or XLSX file in which the differences between the databases will be saved
      -c, --columns         comma-separated list of columns
      -p, --passengerid     comma-separated list of passengers ids
      -v, --verbose         increase output verbosity
      -f, --floatprecision  compare floats using numpy.isclose function
```
#### Input file
Library support csv and json data input. I've made an assumption that json data will look like one exported from an API provided in tasks constrains.

#### Columns
You can specify columns you want to analyze. To do so, provide comma-separated columns names after -c/--columns flag:
```
$ (venv) python TPC.py -i examples/titanic-passengers.csv -o examples/discrepencies.csv -c name,sex,fare -v -f
```

#### PassengerID
Like columns, you can pass passengers whose data you'd like to scan:
```
$ (venv) python TPC.py -i examples/titanic-passengers.csv -o examples/discrepencies.csv -p 90,225,44,183,518 -v
```

#### Float precision
API provided in task constrains sometimes produces results like 'fare = 7.8542000000000005' so I recommend using -f flag to avoid flagging irrelevant differences between floats. If the flag is raised, the comparison will take place using the `numpy.isclose` function. 

#### Excel
Using --excel flag (or -e for short) let you see discrepencies in xlsx file with cells filled with color marking differences between expected and actual data.

```
$ (venv) python TPC.py -i examples/titanic-passengers.csv -o examples/discrepencies.csv -v -f -e examples/Excel_discrepencies.xlsx
```

Running above command will run analysis of given file and output Discrepencies.csv and Discrepencies.xlsx files in ./discrepencies/ directory for you to collect.

## From python script

```python
from TPC import titanic_datasets_comparison, ArgparseFactory

parser = ArgparseFactory()
parser.add_argument("-i examples/titanic-passengers.csv -o examples/discrepencies.csv -f -v -c sex,name,fare") 
args = parser.parse_args()

titanic_datasets_comparison(args)
```

You can also feed the parser with arguments one by one:

```python
from TPC import titanic_datasets_comparison, ArgparseFactory

parser = ArgparseFactory()
parser.add_argument("-i examples/titanic-passengers.csv")
parser.add_argument("-o examples/discrepencies.csv")
parser.add_argument("-f")
parser.add_argument("-v")
parser.add_argument("-c sex,name,fare") 
args = parser.parse_args()

titanic_datasets_comparison(args)
```
## Running examples

```
$ (venv) python TPC.py -i examples/titanic-passengers.csv -o examples/discrepencies.csv -v -f
```

## Running tests

```
$ (venv) python -m pytest -v
```
