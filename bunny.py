from wsgiref.simple_server import make_server


class Bunny:
    controllers = {}

    def handler(self, environ, start_response):
        url_array = environ['PATH_INFO'].split('/')
        if len(self.controllers.keys()) > 0:
            if len(url_array) > 2:
                action = url_array[2].lower()
            else:
                action = 'index'
            response = self.__call_action__(url_array[1], action)
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
            self.controllers[mod_name] = new_ctrl
        if ctrl_cls.__class__.__name__ == 'module':
            mod_name = ctrl_cls.__name__[11:-10].lower()
            self.controllers[mod_name] = ctrl_cls
        if ctrl_cls.__class__.__name__.endswith('Controller'):
            mod_name = ctrl_cls.__class__.__name__[0:-10].lower()
            self.controllers[mod_name] = ctrl_cls

    def run(self):
        httpd = make_server(self.__host__, self.__port__, self.handler)
        information = '''
                                 
 _____                 _____     
| __  |_ _ ___ ___ _ _|  _  |_ _ 
| __ -| | |   |   | | |   __| | |
|_____|___|_|_|_|_|_  |__|  |_  |
                  |___|     |___|
BunnyPy v0.0.4
Serving HTTP on port {1}...
Running on http://{0}:{1}/ (Press CTRL+C to quit)
'''
        print(information.format(self.__host__, self.__port__))
        httpd.serve_forever()

    def __call_action__(self, name, action):
        mod = self.controllers.get(name)
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
