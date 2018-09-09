from wsgiref.simple_server import make_server


class Cobra:
    rules = []

    def application(self, environ, start_response):
        url = environ['PATH_INFO']
        if url.startswith("/static/"):
            try:
                with open(url[1:], "rb") as static_file:
                    data = static_file.read()
            except FileNotFoundError:
                data = b'<h1>404 Not Found</h1>'
            start_response('200 OK', [('Content-Type', 'text/html')])
            return [data]
        for rule in self.rules:
            if rule['path'] == url:
                resp = rule['func']()
                start_response('200 OK', [('Content-Type', 'text/html')])
                return [resp.encode('utf-8')]
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [b'<h1>Welcome to use cobra.py!</h1>', b'<p>cobra.py is successfully working.</p>']

    def route(self, path, **options):
        def decorator(func):
            self.rules.append({'path': path, 'func': func})
            return func

        return decorator

    def run(self):
        httpd = make_server('', 8000, self.application)
        print("Serving HTTP on port 8000...")
        httpd.serve_forever()
