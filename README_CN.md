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
