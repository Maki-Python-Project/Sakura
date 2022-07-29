import inspect
import os

from jinja2 import Environment, FileSystemLoader
from parse import parse
from middleware import Middleware
from webob import Response


class API:
    def __init__(self, templates_dir="templates"):
        self.routes = {}
        self.templates_env = Environment(
            loader=FileSystemLoader(os.path.abspath(templates_dir))
        )
        self.exception_handler = None
        self.middleware = Middleware(self)

    def __call__(self, environ, start_response):
        return self.middleware(environ, start_response)

    def add_middleware(self, middleware_cls):
        self.middleware.add(middleware_cls)

    def add_route(self, path, handler):
        assert path not in self.routes, "Such route already exists."
        self.routes[path] = handler

    def route(self, path):
        if path in self.routes:
            raise AssertionError("Such route already exists.")

        def wrapper(handler):
            self.add_route(path, handler)
            return handler

        return wrapper

    def default_response(self, response):
        response.status_code = 404
        response.text = "Not found."

    def find_handler(self, request_path):
        for path, handler in self.routes.items():
            parse_result = parse(path, request_path)
            if parse_result is not None:
                return handler, parse_result.named

        return None, None

    def handle_request(self, request):
        response = Response()

        handler, kwargs = self.find_handler(request_path=request.path)

        try:
            if handler is not None:
                if inspect.isclass(handler):
                    handler = getattr(handler(), request.method.lower(), None)
                    if handler is None:
                        raise AttributeError("Method now allowed", request.method)

                handler(request, response, **kwargs)
            else:
                self.default_response(response)
        except Exception as e:
            if self.exception_handler is None:
                raise e
            else:
                self.exception_handler(request, response, e)

        return response

    def template(self, template_name, context=None):
        if context is None:
            context = {}

        return self.templates_env.get_template(template_name).render(**context)

    def add_exception_handler(self, exception_handler):
        self.exception_handler = exception_handler

    def get_data_from_form(self, request):
        lst_input_data = []
        dic_data = {}
        body_form = request.body_file
        data = list(body_form)[0]
        str_data = data.decode('UTF-8')
        data = str_data.split('&')
        for el in data:
            idx = el.find('=')
            dic_data[el[:idx]] = el[idx+1:]
            lst_input_data.append(el[idx+1:])
        return {'dict': dic_data, 'list': lst_input_data}
