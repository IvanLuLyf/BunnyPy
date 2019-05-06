from html import escape
from urllib.parse import parse_qs, unquote
from wsgiref.simple_server import make_server


class Bunny:
    __controllers__ = {}
    __queries__ = {}
    __request_body__ = {}
    __path_data__ = []
    request_method = 'GET'

    def handler(self, environ, start_response):
        url_array = environ['PATH_INFO'].split('/')
        if url_array[1] == '':
            url_array[1] = 'index'
        if len(url_array) > 3:
            self.__path_data__ = url_array[3:]
        if len(self.__controllers__.keys()) > 0:
            query_string = environ['QUERY_STRING']
            self.request_method = environ['REQUEST_METHOD']
            if self.request_method != 'GET':
                self.__parse_input__(environ)
            self.__queries__ = parse_qs(query_string)
            if len(url_array) > 2:
                action = url_array[2].lower()
            else:
                action = 'index'
            response = self.__call_action__(url_array[1], action)
            self.__erase_query__()
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return [response.encode('utf-8')]
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

    def controller(self, ctrl_cls):
        if isinstance(ctrl_cls, type):
            new_ctrl = ctrl_cls()
            mod_name = new_ctrl.__class__.__name__[0:-10].lower()
            self.__controllers__[mod_name] = new_ctrl
        if ctrl_cls.__class__.__name__ == 'module':
            mod_name = ctrl_cls.__name__[11:-10].lower()
            self.__controllers__[mod_name] = ctrl_cls
        if ctrl_cls.__class__.__name__.endswith('Controller'):
            mod_name = ctrl_cls.__class__.__name__[0:-10].lower()
            self.__controllers__[mod_name] = ctrl_cls

    def run(self):
        httpd = make_server(self.__host__, self.__port__, self.handler)
        information = '''
                                 
 _____                 _____     
| __  |_ _ ___ ___ _ _|  _  |_ _ 
| __ -| | |   |   | | |   __| | |
|_____|___|_|_|_|_|_  |__|  |_  |
                  |___|     |___|
BunnyPy v0.0.5
Serving HTTP on port {1}...
Running on http://{0}:{1}/ (Press CTRL+C to quit)
'''
        print(information.format(self.__host__, self.__port__))
        httpd.serve_forever()

    def path(self, index, default_val=''):
        if index < len(self.__path_data__):
            return self.__path_data__[index]
        return default_val

    def request(self, name, method='GET', multi_param=False):
        if method == 'GET':
            if multi_param:
                data_arr = self.__queries__.get(name, [])
                return [escape(data) for data in data_arr]
            data = self.__queries__.get(name, [None])[0]
            if data:
                return escape(data)
            return None
        else:
            if multi_param:
                data_arr = self.__request_bodies__.get(name, [])
                return [escape(data) for data in data_arr]
            data = self.__request_bodies__.get(name, [None])[0]
            if data:
                return escape(unquote(data))
            return None

    def __call_action__(self, name, action):
        mod = self.__controllers__.get(name)
        if mod is not None:
            ac = getattr(mod, 'ac_' + action, None)
            if ac is not None:
                return ac()
            else:
                ac_other = getattr(mod, 'other', None)
                if ac_other is not None:
                    return ac_other()
                else:
                    return 'Action {0} Not Exists'.format(action)
        else:
            return 'Mod {0} Not Exists'.format(name)

    def __erase_query__(self):
        self.__queries__ = {}
        self.__request_bodies__ = {}
        self.__path_data__ = []

    def __parse_input__(self, environ):
        try:
            content_length = int(environ['CONTENT_LENGTH'])
        except ValueError:
            content_length = 0
        request_body = environ['wsgi.input'].read(content_length)
        self.__request_bodies__ = parse_qs(request_body.decode('utf-8'), )
