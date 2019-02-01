import re
from wsgiref.simple_server import make_server
from urllib.parse import parse_qs, unquote
from html import escape


class Cobra:
    __rules__ = []
    __queries__ = {}
    __request_bodies__ = {}
    __connection__ = None
    request_method = 'GET'

    def __init__(self, host='127.0.0.1', port=8000, connection=None):
        self.__host = host
        self.__port = port
        self.__connection__ = connection

    def __parse_input(self, environ):
        try:
            content_length = int(environ['CONTENT_LENGTH'])
        except ValueError:
            content_length = 0
        request_body = environ['wsgi.input'].read(content_length)
        self.__request_bodies__ = parse_qs(request_body.decode('utf-8'), )

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

    def __application(self, environ, start_response):
        url = environ['PATH_INFO']
        query_string = environ['QUERY_STRING']
        self.request_method = environ['REQUEST_METHOD']
        if self.request_method != 'GET':
            self.__parse_input(environ)
        self.__queries__ = parse_qs(query_string)
        if url.startswith("/static/"):
            try:
                with open(url[1:], "rb") as static_file:
                    data = static_file.read()
            except FileNotFoundError:
                data = b'<h1>404 Not Found</h1>'
            start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
            return [data]
        for rule in self.__rules__:
            if rule['path'] == url:
                resp = rule['func']()
                start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
                return [resp.encode('utf-8')]
        start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
        return [b'<h1>Welcome to use cobra.py!</h1>', b'<p>cobra.py is successfully working.</p>']

    def route(self, path, **options):
        def decorator(func):
            self.__rules__.append({'path': path, 'func': func})
            return func

        return decorator

    def render(self, view, context=None):
        return self.TemplateRender(view, context).render()

    def run(self):
        httpd = make_server(self.__host, self.__port, self.__application)
        print("Serving HTTP on port {0}...".format(self.__port))
        print("Running on http://{0}:{1}/ (Press CTRL+C to quit)".format(self.__host, self.__port))
        httpd.serve_forever()

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
            where = ' Where ' + where
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
            where = ' Where ' + where
        cursor = self.__connection__.cursor()
        sql_string = "delete from %s %s" % (table, where)
        cursor.execute(sql_string, param)
        result = cursor.rowcount
        self.__connection__.commit()
        cursor.close()
        return result

    def select(self, sql, fetch_all=False):
        def new_select(*args):
            param = list(args)
            if fetch_all:
                return self.fetch_all(sql, param)
            else:
                return self.fetch(sql, param)

        def decorator(func):
            return new_select

        return decorator

    def insert(self, sql=None, table=None):
        def new_insert(*args):
            cursor = self.__connection__.cursor()
            cursor.execute(sql, list(args))
            self.__connection__.commit()
            cursor.close()

        def new_insert_with_table(data):
            return self.insert_into(table, data)

        def decorator(func):
            if table is not None:
                return new_insert_with_table
            elif sql is not None:
                return new_insert
            else:
                return None

        return decorator

    def data(self, model):
        __cobra__ = self

        class DataModel(model):

            def __init__(self, *args, **kws):
                model.__init__(self, *args, **kws)

            def __str__(self):
                return str(vars(self))

            def insert(self):
                return __cobra__.insert_into(str.lower(model.__name__), vars(self))

            @staticmethod
            def get(param=None):
                if param is None:
                    param = []
                data = __cobra__.fetch("select * from " + str.lower(model.__name__), param)
                m = DataModel()
                m.__dict__.update(data)
                return m

            @staticmethod
            def get_all(param=None):
                if param is None:
                    param = []
                result = []
                data = __cobra__.fetch_all("select * from " + str.lower(model.__name__), param)
                for d in data:
                    m = DataModel()
                    m.__dict__.update(d)
                    result.append(m)
                return result

        return DataModel

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
        def __init__(self, view, context=None):
            try:
                with open("template/" + view, "r", encoding='utf-8') as template_file:
                    self.raw_text = template_file.read()
            except FileNotFoundError:
                self.raw_text = '<h1>Template' + view + ' Not Found</h1>'
            self.context = context or {}
            self.data_context = {}
            self.code_builder = code_builder = Cobra.CodeBuilder()
            self.buffered = []

            self.re_variable = re.compile(r'{{ .*? \}\}')
            self.re_comment = re.compile(r'{# .*? #\}')
            self.re_tag = re.compile(r'{% .*? %\}')
            self.re_tokens = re.compile(r'''(
                (?:{{ .*? \}\})
                |(?:{\# .*? \#\})
                |(?:{% .*? %\})
            )''', re.X)

            code_builder.add_line('def __cobra_temp():')
            code_builder.forward()
            code_builder.add_line('__cobra_ret = []')
            self._parse_text()

            self.flush_buffer()
            code_builder.add_line('return "".join(__cobra_ret)')
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
            line = '__cobra_ret.extend([{0}])'.format(','.join(self.buffered))
            self.code_builder.add_line(line)
            self.buffered = []

        def render(self):
            try:
                self.data_context.update(self.context)
                exec(str(self.code_builder), self.data_context)
                result = self.data_context['__cobra_temp']()
                return result
            except NameError as e:
                return str(e)
