from cobra import Cobra

app = Cobra()


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


if __name__ == '__main__':
    app.run()
