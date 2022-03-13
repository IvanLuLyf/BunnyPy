# BunnyPy
a Lightweight Python Web Framework

![BunnyPy](logo.png?raw=true)

[![PyPI](https://img.shields.io/pypi/v/bunnypy.svg?style=flat-square)](https://pypi.org/project/BunnyPy/)
[![Downloads](https://img.shields.io/pypi/dm/bunnypy.svg?color=brightgreen&style=flat-square)](https://pypi.org/project/BunnyPy/)
[![License](https://img.shields.io/pypi/l/bunnypy.svg?color=blue&style=flat-square)](LICENSE)

English | [中文](README_CN.md)

## Installation

```shell
pip install bunnypy
```

## Simple Usage

a HelloWord Application

```python
from bunnypy import Bunny

app = Bunny()

@app.controller
class IndexController:
    def ac_index(self):
        return 'Hello Bunny'

if __name__ == '__main__':
    app.run()
```

## Data Model

```python
from bunnypy import Bunny
import sqlite3

# ------------------------------------------------------------
# Config database using SQLite3

db = Bunny.SQLiteDatabase(sqlite3.connect('test.db'), 'tp_')
app = Bunny(database=db)

# ------------------------------------------------------------
# Declare a Model Class


@app.data
class Message:
    __pk__ = ['id']
    __ai__ = 'id'
    id = 'integer not null'
    msg = 'text not null'

    def __init__(self, msg=None):
        self.msg = msg


# ------------------------------------------------------------
# Create a table

Message.create() # create a table named "tp_message"

# ------------------------------------------------------------
# Insert Data

Message(msg="New Message").insert() # add a new row into table "tp_message"

# ------------------------------------------------------------
# Chained-call style query

# get one row where msg equals "Test"
Message.where(" msg = ? ",["Test"]).get(['id','msg'])

# get 10 rows of data starting at position 0 and sort by id in reverse order
size = 10
start = 0
Message.where().order(' id desc ').limit(size,start).get_all(['id','msg'])

```

## Template

```temp.html``` in ```template``` dir

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Template</title>
</head>
<body>
Output: {{ msg }}
</body>
</html>
```

Python code

```python
from bunnypy import Bunny

app = Bunny()

@app.controller
class IndexController:
    def ac_index(self):
        return app.render('temp.html',{"msg":"Hello World"})


if __name__ == '__main__':
    app.run()

```