from wsgiref.simple_server import make_server


class Bunny:
    rules = []

    def handler(self, environ, start_response):
        if len(self.rules) > 0:
            url = environ['PATH_INFO']
            for rule in self.rules:
                if rule['path'] == url:
                    response = rule['func']()
                    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
                    return [response.encode('utf-8')]
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return ['Page Not Found'.encode('utf-8')]
        else:
            default_html = '''
<h1>Welcome to <a href="https://github.com/IvanLuLyf/BunnyPy">BunnyPy</a>!</h1>
<p>If you see this page, the BunnyPy is successfully working.</p>
<p><em>Thank you for using BunnyPy.</em></p>'''
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return [default_html.encode('utf-8')]

    def __init__(self, host='127.0.0.1', port=8000, connection=None, database_type='sqlite'):
        self.__host__ = host
        self.__port__ = port
        self.__connection__ = connection
        self.__database_type__ = database_type

    def route(self, path, **options):
        def decorator(func):
            self.rules.append({'path': path, 'func': func})
            return func

        return decorator

    def run(self):
        httpd = make_server(self.__host__, self.__port__, self.handler)
        print('BunnyPy v0.0.2')
        print("Serving HTTP on port {0}...".format(self.__port__))
        print("Running on http://{0}:{1}/ (Press CTRL+C to quit)".format(self.__host__, self.__port__))
        httpd.serve_forever()
