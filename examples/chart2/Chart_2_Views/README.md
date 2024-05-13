# Demonstrates creating charts.

![charts_happy](https://user-images.githubusercontent.com/4193389/198873533-36de5d26-1071-467b-95f4-2e557b4017cb.png)

Demonstrates loading a spread sheet into Calc and dynamically inserting charts using `Chart2` class.
There are a total of 17 different charts that can be dynamically created by this demo.

A message box is display once the document has been created asking if you want to close the document.

## NOTE

There is currently a [bug](https://bugs.documentfoundation.org/show_bug.cgi?id=151846) in LibreOffice `7.4` that does not allow the `Chart2` class to load.
The `Chart2` has been tested with LibreOffice `7.3` and LibreOffice >= `7.5`


## Options

The type of chart created is determined by the `-k` option.

Possible `-k` options are:

- area
- bar
- bubble_labeled
- col
- col_line
- col_multi
- donut
- happy_stock
- line
- lines
- net
- pie
- pie_3d
- scatter
- scatter_line_error
- scatter_line_log
- stock_prices
- default

## Automate

### Cross Platform

From current example folder.

```sh
python -m start -k happy_stock
```

### Linux/Mac

```sh
python ./tests/samples/Chart2/Chart_2_Views/start.py -k happy_stock
```

### Windows

```ps
python .\tests\samples\Chart2\Chart_2_Views\start.py -k happy_stock
```
