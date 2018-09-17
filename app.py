from cobra import Cobra
import sqlite3

app = Cobra(connection=sqlite3.connect('test.db'))


@app.route('/index')
def index():
    return "<h1>Hello World</h1>"


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
    l = '<br>'.join([str(d) for d in data])
    return l + '''
    <form action="users" method="POST">
        <input type="text" name="name">
        <input type="submit" value="Submit">
    </form>
    '''


if __name__ == '__main__':
    app.run()
