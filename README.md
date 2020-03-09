# BunnyPy
a Lightweight Python Web Framework

![BunnyPy](bunny.png?raw=true)

[![PyPI](https://img.shields.io/pypi/v/bunnypy.svg?style=flat-square)](https://pypi.org/project/BunnyPy/)
[![Downloads](https://img.shields.io/pypi/dm/bunnypy.svg?color=brightgreen&style=flat-square)](https://pypi.org/project/BunnyPy/)
[![License](https://img.shields.io/pypi/l/bunnypy.svg?color=blue&style=flat-square)](LICENSE)

English | [中文](README_CN.md)

## Installation

```shell
pip install bunnypy
```

## Simple Usage

> hello.py

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

### Config database

Example: using SQLite3

```python
from bunnypy import Bunny
import sqlite3

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

Message.create() # create a table

# ------------------------------------------------------------
# Insert Data

Message(msg="New Message").insert() # add a new row into table

# ------------------------------------------------------------
# Linked call query

size = 10
start = 0

Message.where(" msg = ? ",["Test"]).order(' id desc ').limit(size,start).get(['id','msg'])

# or

Message.where(" msg = ? ",["Test"]).order(' id desc ').limit(size,start).get_all(['id','msg'])

```