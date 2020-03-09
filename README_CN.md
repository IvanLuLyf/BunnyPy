# BunnyPy
轻量级的Python Web框架

![BunnyPy](bunny.png?raw=true)

[![PyPI](https://img.shields.io/pypi/v/bunnypy.svg?style=flat-square)](https://pypi.org/project/BunnyPy/)
[![Downloads](https://img.shields.io/pypi/dm/bunnypy.svg?color=brightgreen&style=flat-square)](https://pypi.org/project/BunnyPy/)
[![License](https://img.shields.io/pypi/l/bunnypy.svg?color=blue&style=flat-square)](LICENSE)

[English](README.md) | 中文

## 安装

```shell
pip install bunnypy
```

## 简单使用

一个HelloWorld应用

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

## 数据模型

```python
from bunnypy import Bunny
import sqlite3

# ------------------------------------------------------------
# 使用SQLite3配置数据库

db = Bunny.SQLiteDatabase(sqlite3.connect('test.db'), 'tp_')
app = Bunny(database=db)

# ------------------------------------------------------------
# 声明一个数据模型类


@app.data
class Message:
    __pk__ = ['id']
    __ai__ = 'id'
    id = 'integer not null'
    msg = 'text not null'

    def __init__(self, msg=None):
        self.msg = msg


# ------------------------------------------------------------
# 创建表格

Message.create() # 创建一个名为"tp_message"的表

# ------------------------------------------------------------
# 插入数据

Message(msg="New Message").insert() # 在"tp_message"表添加一行数据

# ------------------------------------------------------------
# 链式调用查询

# 获取msg等于"Test"的一行数据
Message.where(" msg = ? ",["Test"]).get(['id','msg'])

# 从位置0开始获取十行数据并按ID倒序
size = 10
start = 0
Message.where().order(' id desc ').limit(size,start).get_all(['id','msg'])

```

## 模板

在```template```目录下的```temp.html```

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

对应的Python代码

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