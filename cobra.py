from wsgiref.simple_server import make_server
from urllib.parse import parse_qs, unquote
from html import escape


class Cobra:
    __rules = []
    __queries = {}
    __request_bodies = {}
    request_method = 'GET'

    def __init__(self, host='127.0.0.1', port=8000):
        self.__host = host
        self.__port = port

    def __parse_input(self, environ):
        try:
            content_length = int(environ['CONTENT_LENGTH'])
        except ValueError:
            content_length = 0
        request_body = environ['wsgi.input'].read(content_length)
        self.__request_bodies = parse_qs(request_body.decode('utf-8'),)

    def request(self, name, method='GET', multi_param=False):
        if method == 'GET':
            if multi_param:
                data_arr = self.__queries.get(name, [])
                return [escape(data) for data in data_arr]
            data = self.__queries.get(name, [None])[0]
            if data:
                return escape(data)
            return None
        else:
            if multi_param:
                data_arr = self.__request_bodies.get(name, [])
                return [escape(data) for data in data_arr]
            data = self.__request_bodies.get(name, [None])[0]
            if data:
                return escape(unquote(data))
            return None

    def __application(self, environ, start_response):
        url = environ['PATH_INFO']
        query_string = environ['QUERY_STRING']
        self.request_method = environ['REQUEST_METHOD']
        if self.request_method != 'GET':
            self.__parse_input(environ)
        self.__queries = parse_qs(query_string)
        if url.startswith("/static/"):
            try:
                with open(url[1:], "rb") as static_file:
                    data = static_file.read()
            except FileNotFoundError:
                data = b'<h1>404 Not Found</h1>'
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return [data]
        for rule in self.__rules:
            if rule['path'] == url:
                resp = rule['func']()
                start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
                return [resp.encode('utf-8')]
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
        return [b'<h1>Welcome to use cobra.py!</h1>', b'<p>cobra.py is successfully working.</p>']

    def route(self, path, **options):
        def decorator(func):
            self.__rules.append({'path': path, 'func': func})
            return func

        return decorator

    def run(self):
        httpd = make_server(self.__host, self.__port, self.__application)
        print("Serving HTTP on port {0}...".format(self.__port))
        print("Running on http://{0}:{1}/ (Press CTRL+C to quit)".format(self.__host, self.__port))
        httpd.serve_forever()
