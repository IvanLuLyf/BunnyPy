# Cobra.py
该项目用于学习如何使用wsgiref来创建一个网站服务。

# 简单使用

```python
from cobra import Cobra

app = Cobra()

@app.route('/index')
def index():
    return "<h1>Hello World</h1>"


if __name__ == '__main__':
    app.run()
```

# 在Cobra.py中使用数据库
```python
from cobra import Cobra
import sqlite3 #you can also using database driver that can using Cursor

app = Cobra(connection=sqlite3.connect('test.db'))

@app.route("/users")
def db():
    @app.select("select * from user", fetch_all=True)
    def get_all():
        pass

    @app.insert("insert into user (name) values (?)")
    def insert_user(name):
        pass

    name = app.request("name", method='POST')
    if name:
        insert_user(name)
    data = get_all()
    return '<br>'.join([str(d) for d in data]) + '''
    <form action="users" method="POST">
        <input type="text" name="name">
        <input type="submit" value="Submit">
    </form>
    '''
```

# 使用Cobra数据模型
```python

from cobra import Cobra
import sqlite3 #you can also using database driver that can using Cursor

app = Cobra(connection=sqlite3.connect('test.db'))

# 装饰器
@app.data
class User:
    def __init__(self, name=None):
        self.name = name

@app.route("/users")
def users():
    data = User.get_all()
    l = '<br>'.join([str(d) for d in data])
    return l + '''
    <form action="users" method="POST">
        <input type="text" name="name">
        <input type="submit" value="Submit">
    </form>
    '''


if __name__ == '__main__':
    app.run()

```

# Cobra模板
> temp.html
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Template</title>
</head>
<body>
输出: {{ msg }}
</body>
</html>
```
> Python code
```python

from cobra import Cobra

app = Cobra()

@app.route("/temp")
def temp():
    return app.render('temp.html',{"msg":"Hello World"})


if __name__ == '__main__':
    app.run()

```