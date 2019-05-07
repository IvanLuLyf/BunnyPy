# BunnyPy
a Lightweight Python Web Framework

![PyPI](https://img.shields.io/pypi/v/bunnypy.svg?style=flat-square)
![Downloads](https://img.shields.io/pypi/dm/bunnypy.svg?color=brightgreen&style=flat-square)
![License](https://img.shields.io/pypi/l/bunnypy.svg?color=blue&style=flat-square)

## Installation

```shell
pip install bunnypy
```

## Simple Usage

> hello.py

```python
from bunny import Bunny

app = Bunny()

@app.controller
class IndexController:
    def ac_index(self):
        return 'Hello World'

if __name__ == '__main__':
    app.run()
```

