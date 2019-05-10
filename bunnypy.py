import re
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
        if url_array[1] == 'static':
            try:
                with open(environ['PATH_INFO'][1:], "rb") as static_file:
                    data = static_file.read()
            except FileNotFoundError:
                data = b'<h1>404 Not Found</h1>'
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            self.__erase_query__()
            return [data]
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

    def __init__(self, host='127.0.0.1', port=8000, database=None):
        if database is None:
            database = {}
        db_config = {'connection': None, 'type': 'sqlite', 'prefix': ''}
        db_config.update(database)
        self.__host__ = host
        self.__port__ = port
        self.__connection__ = db_config['connection']
        self.__database_type__ = db_config['type']
        self.__database_prefix__ = db_config['prefix']

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
BunnyPy v0.1.0
Serving HTTP on port {1}...
Running on http://{0}:{1}/ (Press CTRL+C to quit)
'''
        print(information.format(self.__host__, self.__port__))
        httpd.serve_forever()

    def path(self, index, default_val=''):
        if index < len(self.__path_data__):
            return self.__path_data__[index]
        return default_val

    def request(self, name, method='GET', default_val=None, multi_param=False):
        if method == 'GET':
            if multi_param:
                data_arr = self.__queries__.get(name, [])
                return [escape(data) for data in data_arr]
            data = self.__queries__.get(name, [None])[0]
            if data:
                return escape(data)
            return default_val
        else:
            if multi_param:
                data_arr = self.__request_bodies__.get(name, [])
                return [escape(data) for data in data_arr]
            data = self.__request_bodies__.get(name, [None])[0]
            if data:
                return escape(unquote(data))
            return default_val

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

    def data(self, model):
        __bunny__ = self

        class DataModel(model):
            def __init__(self, *args, **kws):
                model.__init__(self, *args, **kws)

            def __str__(self):
                return str(vars(self))

            def insert(self):
                return __bunny__.insert_into(self.table_name(), vars(self))

            @staticmethod
            def table_name():
                if '__table__' in model.__dict__:
                    return model.__table__
                model_name = model.__name__
                if model_name.endswith('Model'):
                    model_name = model_name[0:-5]
                p = re.compile(r'([a-z]|\d)([A-Z])')
                return __bunny__.__database_prefix__ + re.sub(p, r'\1_\2', model_name).lower()

            @staticmethod
            def create():
                __structure__ = []
                primary_keys = ''
                table_name = DataModel.table_name()
                if self.__database_type__ == 'mysql':
                    for v in model.__dict__:
                        if not str.startswith(v, '__'):
                            column = v + " " + model.__dict__[v]
                            if '__ai__' in model.__dict__ and v == model.__ai__:
                                column += ' auto_increment '
                            __structure__.append(column)
                        if '__pk__' in model.__dict__:
                            primary_keys = ',primary key(%s)' % (','.join(model.__pk__))
                    sql = "create table %s (%s %s)" % (table_name, ','.join(__structure__), primary_keys)
                else:
                    for v in model.__dict__:
                        if not str.startswith(v, '__'):
                            column = v + " " + model.__dict__[v]
                            if '__pk__' in model.__dict__ and v in model.__pk__:
                                column += ' primary key '
                            if '__ai__' in model.__dict__ and v == model.__ai__:
                                column += ' autoincrement '
                            __structure__.append(column)
                    sql = "create table %s (%s)" % (table_name, ','.join(__structure__))
                cursor = self.__connection__.cursor()
                try:
                    cursor.execute(sql)
                    cursor.close()
                    return True
                except Exception:
                    cursor.close()
                    return False

        return DataModel

    def fetch(self, sql, param=None):
        if param is None:
            param = []
        cursor = self.__connection__.cursor()
        cursor.execute(sql, param)
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        cursor.close()
        return dict(zip(columns, row))

    def fetch_all(self, sql, param=None):
        if param is None:
            param = []
        cursor = self.__connection__.cursor()
        cursor.execute(sql, param)
        columns = [desc[0] for desc in cursor.description]
        values = cursor.fetchall()
        cursor.close()
        result = []
        for row in values:
            result.append(dict(zip(columns, row)))
        return result

    def insert_into(self, table, data):
        keys = list(data.keys())
        values = list(data.values())
        sql_string = "insert into %s (%s) values(%s)" % (
            table, ','.join(keys), ','.join(['?' for i in range(len(keys))]))
        cursor = self.__connection__.cursor()
        cursor.execute(sql_string, values)
        self.__connection__.commit()
        cursor.close()

    def update_by(self, data, table, where=None, param=None):
        if param is None:
            param = []
        if where is not None:
            where = ' where ' + where
        cursor = self.__connection__.cursor()
        keys = list(data.keys())
        values = list(data.values())
        sets = ','.join([keys[i] + '=?' for i in range(len(keys))])
        sql_string = "update %s set %s %s" % (table, sets, where)
        values.extend(param)
        cursor.execute(sql_string, values)
        result = cursor.rowcount
        self.__connection__.commit()
        cursor.close()
        return result

    def delete_by(self, table, where=None, param=None):
        if param is None:
            param = []
        if where is not None:
            where = ' where ' + where
        cursor = self.__connection__.cursor()
        sql_string = "delete from %s %s" % (table, where)
        cursor.execute(sql_string, param)
        result = cursor.rowcount
        self.__connection__.commit()
        cursor.close()
        return result
