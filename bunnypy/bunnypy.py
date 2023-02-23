import json
import os
import re
import traceback
from html import escape
from pathlib import Path
from urllib.parse import parse_qs
from wsgiref.simple_server import make_server

__version__ = "0.3.0"

__default_html__ = '''<html lang="en"><head><meta charset="utf-8"><title>Welcome to BunnyPy</title>
<style>body{width: 35em;margin: 0 auto;text-align: center;}</style></head><body>
<a href="https://github.com/IvanLuLyf/BunnyPy">
<img src="https://github.com/IvanLuLyf/BunnyPy/raw/master/logo.png?raw=true" width="400px" style="margin-top: 150px">
</a>
<h1>Welcome to <a href="https://github.com/IvanLuLyf/BunnyPy">BunnyPy</a>!</h1>
<p>If you see this page, the BunnyPy is successfully working.</p>
<p><em>Thank you for using BunnyPy.</em></p></body></html>'''

__running_msg__ = '''

 _____                 _____     
| __  |_ _ ___ ___ _ _|  _  |_ _ 
| __ -| | |   |   | | |   __| | |
|_____|___|_|_|_|_|_  |__|  |_  |
                  |___|     |___|
BunnyPy v{0}
Serving HTTP on port {1}...
Running on http://{1}:{2}/ (Press CTRL+C to quit)

'''

__asset_dir__ = os.path.dirname(os.path.abspath(__file__)) + '/asset/'
__def_allowed_methods__ = ', '.join(['GET', 'POST', 'PUT', 'DELETE'])
__def_allowed_headers__ = ', '.join(['Content-Type', 'Authorization'])


class Bunny:
    __sub_apps__ = {}
    __controllers__ = {}
    request_method = 'GET'

    def handler(self, environ, start_response):
        if callable(self.__cors__):
            cors_conf = self.__cors__(environ)
        else:
            cors_conf = {}
        allowed_origin = cors_conf['origins'] if 'origins' in cors_conf else ''
        if environ['REQUEST_METHOD'] == 'OPTIONS' and 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in environ:
            start_response('200 OK', [
                ('Access-Control-Allow-Origin', allowed_origin),
                ('Access-Control-Allow-Methods', __def_allowed_methods__),
                ('Access-Control-Allow-Headers', __def_allowed_headers__),
                ('Access-Control-Max-Age', '86400')
            ])
            return []
        file_path = Path("static" + environ['PATH_INFO'])
        if file_path.is_file():
            try:
                with file_path.open("rb") as static_file:
                    data = static_file.read()
            except FileNotFoundError:
                data = self.__render_error('404 Not Found')
            start_response('200 OK', [('Access-Control-Allow-Origin', allowed_origin),
                                      ('Content-Type', 'text/html;charset=utf-8')])
            return [data]
        url_array = environ['PATH_INFO'].split('/')
        if url_array[1] == '':
            url_array[1] = 'index'
        if len(self.__controllers__.keys()) > 0:
            if len(url_array) > 2:
                action = url_array[2].lower()
            else:
                action = 'index'
            req = self.Request(environ)
            response = self.__call_action__(req, url_array[1], action)
            if type(response) == dict or type(response) == list:
                start_response('200 OK', [('Access-Control-Allow-Origin', allowed_origin),
                                          ('Content-Type', 'application/json;charset=utf-8')])
                return [json.dumps(response).encode('utf-8')]
            else:
                start_response('200 OK', [('Access-Control-Allow-Origin', allowed_origin),
                                          ('Content-Type', 'text/html;charset=utf-8')])
                return [response.encode('utf-8')]
        else:
            start_response('200 OK', [('Access-Control-Allow-Origin', allowed_origin),
                                      ('Content-Type', 'text/html;charset=utf-8')])
            return [__default_html__.encode('utf-8')]

    def __init__(self, host='127.0.0.1', port=8000, database=None, cors=None):
        self.__host__ = host
        self.__port__ = port
        if isinstance(database, self.Database):
            self.__database__ = database
        if callable(cors):
            self.__cors__ = cors

    def sub_app(self, app_path, app_module):
        pass

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
        _tmp_host = '127.0.0.1' if self.__host__ == '0.0.0.0' else self.__host__
        print(__running_msg__.format(__version__, _tmp_host, self.__port__))
        httpd.serve_forever()

    def __call_action__(self, req, name, action):
        mod = self.__controllers__.get(name)
        if mod is not None:
            ac = getattr(mod, 'ac_' + action, None)
            if ac is not None:
                return self.__call_func__(ac, req)
            else:
                ac_other = getattr(mod, 'other', None)
                if ac_other is not None:
                    return self.__call_func__(ac_other, req)
                else:
                    return self.__render_error('Action {0} Not Exists'.format(action))
        else:
            return self.__render_error('Mod {0} Not Exists'.format(name))

    def __call_func__(self, func, req):
        try:
            args = []
            for i in range(func.__code__.co_argcount):
                vn = func.__code__.co_varnames[i]
                if vn in func.__annotations__:
                    if func.__annotations__[vn] == self.Request:
                        args.append(req)
                    elif func.__annotations__[vn] == int:
                        args.append(int(req[vn]))
                elif vn == 'self':
                    continue
                else:
                    args.append(req[vn])
            return func(*args)
        except Exception as e:
            err_trace = []
            err_origin = traceback.extract_tb(e.__traceback__)
            _no = 0
            for i in err_origin:
                if _no == 0:
                    _no += 1
                    continue
                err_trace.append({
                    "no": _no,
                    "line": i.lineno,
                    "file": str.replace(i.filename, os.sep, '/'),
                    "code": i.line,
                })
                _no += 1
            return self.__render_error(str(e), err_trace)

    def render(self, view, context=None):
        return self.TemplateRender(view, context).render()

    def __render_error(self, msg, err_trace=None):
        return self.TemplateRender('error.html', {
            'bunny_error': msg, 'bunny_error_trace': err_trace
        }, __asset_dir__).render()

    class Request:
        def __init__(self, environ):
            query_string = environ['QUERY_STRING']
            self.method = str.lower(environ['REQUEST_METHOD'])
            self.contentType = environ['CONTENT_TYPE']
            self.query = parse_qs(query_string)
            try:
                content_length = int(environ['CONTENT_LENGTH'])
            except ValueError:
                content_length = 0
            request_body = (environ['wsgi.input'].read(content_length)).decode('utf-8')
            self.__request_body__ = parse_qs(query_string)
            if self.contentType == 'application/json' and content_length > 0:
                self.__request_body__.update(json.loads(request_body))
            else:
                self.__request_body__.update(parse_qs(request_body))

        def __getitem__(self, item):
            if self.contentType == 'application/json':
                return self.__request_body__.get(item, None)
            else:
                data = self.__request_body__.get(item, [None])[0]
                if data:
                    return escape(data)

    def data(self, model):
        __bunny__ = self
        __db__ = self.__database__

        class DataBuilder:
            def __init__(self, where=None, param=None):
                if where is not None:
                    self.__filter__ = where
                    self.__where__ = ' where '
                else:
                    self.__filter__ = ''
                    self.__where__ = ''
                if param is not None:
                    self.__param__ = param
                else:
                    self.__param__ = []

            def limit(self, size, start=0):
                self.__filter__ += " limit {0} offset {1} ".format(size, start)
                return self

            def order(self, order_param):
                self.__filter__ += " order by {0} ".format(order_param)
                return self

            def get(self, columns=None, debug=False, raw=False):
                __c__ = '*'
                if isinstance(columns, list):
                    __c__ = ','.join(columns)
                elif isinstance(columns, str):
                    __c__ = columns
                __f__ = self.__where__ + self.__filter__
                __sql__ = "select {0} from {1}{2}".format(__c__, DataModel.table_name(), __f__)
                data = __db__.fetch(__sql__, self.__param__, debug)
                if raw:
                    return data
                if data is not None:
                    m = DataModel()
                    m.__dict__.update(data)
                    return m
                else:
                    return None

            def get_all(self, columns=None, debug=False, raw=False):
                result = []
                __c__ = '*'
                if isinstance(columns, list):
                    __c__ = ','.join(columns)
                elif isinstance(columns, str):
                    __c__ = columns
                __f__ = self.__where__ + self.__filter__
                __sql__ = "select {0} from {1}{2}".format(__c__, DataModel.table_name(), __f__)
                data = __db__.fetch_all(__sql__, self.__param__, debug)
                if raw:
                    return data
                for d in data:
                    m = DataModel()
                    m.__dict__.update(d)
                    result.append(m)
                return result

            def update(self, data=None, debug=False):
                return __db__.update_by(data, DataModel.table_name(), self.__filter__, self.__param__, debug)

            def delete(self, debug=False):
                return __db__.delete_by(DataModel.table_name(), self.__filter__, self.__param__, debug)

        class DataModel(model):
            def __init__(self, *args, **kws):
                model.__init__(self, *args, **kws)

            def __str__(self):
                return str(vars(self))

            def insert(self, debug=False):
                return __db__.insert_into(vars(self), self.table_name(), debug)

            @staticmethod
            def where(where=None, param=None):
                return DataBuilder(where, param)

            @staticmethod
            def table_name():
                if '__table__' in model.__dict__:
                    return model.__table__
                model_name = model.__name__
                if model_name.endswith('Model'):
                    model_name = model_name[0:-5]
                p = re.compile(r'([a-z]|\d)([A-Z])')
                return __db__.prefix() + re.sub(p, r'\1_\2', model_name).lower()

            @staticmethod
            def create(debug=False):
                table_name = DataModel.table_name()
                columns = {}
                ai = ''
                pk = []
                uk = None
                for v in model.__dict__:
                    if not str.startswith(v, '__'):
                        columns[v] = model.__dict__[v]
                if '__ai__' in model.__dict__:
                    ai = model.__ai__
                if '__pk__' in model.__dict__:
                    pk = model.__pk__
                if '__uk__' in model.__dict__:
                    uk = model.__uk__
                return __db__.create_table(table_name, columns, pk, ai, uk, debug)

        return DataModel

    class Database:
        def prefix(self) -> str:
            pass

        def fetch(self, sql: str, param: object = None, debug: bool = False) -> dict:
            pass

        def fetch_all(self, sql: str, param: object = None, debug: bool = False) -> list:
            pass

        def insert_into(self, data: dict, table: str, debug: bool = False) -> int:
            pass

        def update_by(self, data: dict, table: str, where: str = None, param: list = None, debug: bool = False) -> int:
            pass

        def delete_by(self, table: str, where: str = None, param: list = None, debug: bool = False) -> int:
            pass

        def create_table(self, tbl: str, cols: dict, pk: list, ai: str = '', uk: list = None, d: bool = False) -> bool:
            pass

        def exec(self, sql: str):
            pass

        def query(self, sql: str) -> object:
            pass

    class PdaDatabase(Database):
        def __init__(self, connection, prefix=''):
            self.__connection__ = connection
            self.__prefix__ = prefix

        def prefix(self):
            return self.__prefix__

        def fetch(self, sql, param=None, debug=False):
            if debug:
                return sql
            if param is None:
                param = []
            cursor = self.__connection__.cursor()
            cursor.execute(sql, param)
            columns = [desc[0] for desc in cursor.description]
            row = cursor.fetchone()
            cursor.close()
            if row is not None:
                return dict(zip(columns, row))
            return None

        def fetch_all(self, sql, param=None, debug=False):
            if debug:
                return sql
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

        def insert_into(self, data, table, debug=False):
            keys = list(data.keys())
            values = list(data.values())
            places = ['?' for i in range(len(keys))]
            sql_string = "insert into {0} ({1}) values({2})".format(table, ','.join(keys), ','.join(places))
            if debug:
                return sql_string
            cursor = self.__connection__.cursor()
            cursor.execute(sql_string, values)
            self.__connection__.commit()
            cursor.close()

        def update_by(self, data, table, where=None, param=None, debug=False):
            if param is None:
                param = []
            if where is not None:
                where = ' where ' + where
            cursor = self.__connection__.cursor()
            keys = list(data.keys())
            values = list(data.values())
            sets = ','.join([keys[i] + '=?' for i in range(len(keys))])
            sql_string = "update {0} set {1} {2}".format(table, sets, where)
            if debug:
                return sql_string
            values.extend(param)
            cursor.execute(sql_string, values)
            result = cursor.rowcount
            self.__connection__.commit()
            cursor.close()
            return result

        def delete_by(self, table, where=None, param=None, debug=False):
            if param is None:
                param = []
            if where is not None:
                where = ' where ' + where
            cursor = self.__connection__.cursor()
            sql_string = "delete from {0} {1}".format(table, where)
            if debug:
                return sql_string
            cursor.execute(sql_string, param)
            result = cursor.rowcount
            self.__connection__.commit()
            cursor.close()
            return result

    class SQLiteDatabase(PdaDatabase):
        def create_table(self, table_name, columns, pk=None, ai='', uk=None, debug=False):
            if pk is None:
                pk = []
            if uk is None:
                uk = []
            __structure__ = []
            __pk__ = ''
            __uk__ = ''
            for c in columns:
                column = c + " " + columns[c]
                if c == ai:
                    column = c + ' integer primary key autoincrement '
                __structure__.append(column)
            if len(pk) > 0 and ai == '':
                __pk__ = ',primary key(' + ','.join(pk) + ')'
            if len(uk) > 0:
                __uk__ = ',unique key(' + ','.join(uk) + ')'
            sql = "create table {0} ({1}{2}{3})".format(table_name, ','.join(__structure__), __pk__, __uk__)
            if debug:
                return sql
            cursor = self.__connection__.cursor()
            try:
                cursor.execute(sql)
                self.__connection__.commit()
                cursor.close()
                return True
            except Exception:
                cursor.close()
                return False

    class CodeBuilder:
        INDENT_STEP = 4

        def __init__(self):
            self.indent = 0
            self.lines = []

        def forward(self):
            self.indent += self.INDENT_STEP

        def backward(self):
            self.indent -= self.INDENT_STEP

        def add(self, code):
            self.lines.append(code)

        def add_line(self, code):
            self.lines.append(' ' * self.indent + code)

        def __str__(self):
            return '\n'.join(map(str, self.lines))

    class TemplateRender:
        def __init__(self, view, context=None, base_path=None):
            if base_path is None:
                base_path = "template/"
            try:
                with open(base_path + view, "r", encoding='utf-8') as template_file:
                    self.raw_text = template_file.read()
            except FileNotFoundError:
                self.raw_text = '<h1>Template' + view + ' Not Found</h1>'
            self.context = context or {}
            self.data_context = {}
            self.code_builder = code_builder = Bunny.CodeBuilder()
            self.buffered = []

            self.re_variable = re.compile(r'{{ .*? \}\}')
            self.re_comment = re.compile(r'{# .*? #\}')
            self.re_tag = re.compile(r'{% .*? %\}')
            self.re_tokens = re.compile(r'''(
                (?:{{ .*? \}\})
                |(?:{\# .*? \#\})
                |(?:{% .*? %\})
            )''', re.X)

            code_builder.add_line('def __bunny_clara_temp():')
            code_builder.forward()
            code_builder.add_line('__bunny_clara_ret = []')
            self._parse_text()

            self.flush_buffer()
            code_builder.add_line('return "".join(__bunny_clara_ret)')
            code_builder.backward()

        def _parse_text(self):
            tokens = self.re_tokens.split(self.raw_text)
            handlers = (
                (self.re_variable.match, self._handle_variable),
                (self.re_tag.match, self._handle_tag),
                (self.re_comment.match, self._handle_comment),
            )
            default_handler = self._handle_string

            for token in tokens:
                for match, handler in handlers:
                    if match(token):
                        handler(token)
                        break
                else:
                    default_handler(token)

        def _handle_variable(self, token):
            variable = token.strip('{} ')
            self.data_context[variable] = ''
            self.buffered.append('str({})'.format(variable))

        def _handle_comment(self, token):
            pass

        def _handle_string(self, token):
            self.buffered.append('{}'.format(repr(token)))

        def _handle_tag(self, token):
            self.flush_buffer()
            tag = token.strip('{%} ')
            tag_name = tag.split()[0]
            self._handle_statement(tag, tag_name)

        def _handle_statement(self, tag, tag_name):
            if tag_name in ('if', 'elif', 'else', 'for'):
                if tag_name in ('elif', 'else'):
                    self.code_builder.backward()
                self.code_builder.add_line('{}:'.format(tag))
                self.code_builder.forward()
            elif tag_name in ('break',):
                self.code_builder.add_line(tag)
            elif tag_name in ('endif', 'endfor'):
                self.code_builder.backward()

        def flush_buffer(self):
            line = '__bunny_clara_ret.extend([{0}])'.format(','.join(self.buffered))
            self.code_builder.add_line(line)
            self.buffered = []

        def render(self):
            try:
                self.data_context.update(self.context)
                exec(str(self.code_builder), self.data_context)
                result = self.data_context['__bunny_clara_temp']()
                return result
            except NameError as e:
                return str(e)
