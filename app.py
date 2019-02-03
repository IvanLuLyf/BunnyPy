from cobra import Cobra
import sqlite3

app = Cobra(connection=sqlite3.connect('test.db'))


@app.data
class User:
    __pk__ = ['id']
    __ai__ = 'id'
    id = 'integer not null'
    name = 'text not null'

    def __init__(self, name=None):
        self.name = name


@app.route('/index')
def index():
    return "<h1>Hello World</h1>"


@app.route('/install')
def install():
    if User.make_table():
        return "Install OK"
    else:
        return "Install Failed"


@app.route('/hi')
def hi():
    if app.request_method == 'GET':
        return '''
        <form action="hi" method="POST">
            <input type="text" name="name">
            <input type="submit" value="Submit">
        </form>
        '''
    else:
        name = app.request("name", method='POST')
        if name:
            return "<h1>Hi!" + name + "</h1>"
        return "<h1>No Data</h1>"


@app.route("/users")
def users():
    name = app.request("name", method='POST')
    if name:
        User(name).insert()
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
