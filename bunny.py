from wsgiref.simple_server import make_server


class Bunny:
    def handler(self, environ, start_response):
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
        return [("Hello BunnyPy in " + self.__host__).encode('utf-8')]

    def __init__(self, host='127.0.0.1', port=8000, connection=None, database_type='sqlite'):
        self.__host__ = host
        self.__port__ = port
        self.__connection__ = connection
        self.__database_type__ = database_type

    def run(self):
        httpd = make_server(self.__host__, self.__port__, self.handler)
        print("Serving HTTP on port {0}...".format(self.__port__))
        print("Running on http://{0}:{1}/ (Press CTRL+C to quit)".format(self.__host__, self.__port__))
        httpd.serve_forever()
