# Cobra.py
This project is made for learning how to build a web server with wsgiref.

# Simple Usage

```python
from cobra import Cobra

app = Cobra()

@app.route('/index')
def index():
    return "<h1>Hello World</h1>"


if __name__ == '__main__':
    app.run()
```