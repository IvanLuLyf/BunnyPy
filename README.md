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

# Using Cobra.py with database
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

# Cobra Data Model
```python

from cobra import Cobra
import sqlite3 #you can also using database driver that can using Cursor

app = Cobra(connection=sqlite3.connect('test.db'))

# decorate class
@app.data
class User:
    __pk__ = ['id']
    __ai__ = 'id'
    id = 'integer not null'
    name = 'text not null'

    def __init__(self, name=None):
        self.name = name

# You can use User.make_table() to create a table
# You can use User("Test").insert() to add a new row into table
# You can use User.get(name = 'test') to get a row that fit the condition
# You can use User.get_all(name = 'test') to get any rows that fit the condition

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

# Cobra Template
> temp.html
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