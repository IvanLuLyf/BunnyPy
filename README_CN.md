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