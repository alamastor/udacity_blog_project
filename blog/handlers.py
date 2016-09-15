import os

import webapp2
import jinja2

import auth
from models import User


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
)


class Handler(webapp2.RequestHandler):

    def write(self, *args, **kwargs):
        self.response.write(*args, **kwargs)

    def render_str(self, template, **kwargs):
        t = jinja_env.get_template(template)
        return t.render(kwargs)

    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def set_cookie(self, name, val):
        self.response.set_cookie(name, val, path='/')


class AuthHandler(webapp2.RequestHandler):

    def initialize(self, *args, **kwargs):
        super(AuthHandler, self).initialize(*args, **kwargs)
        user_id = self.read_secure_cookie('sess')
        self.user = user_id and User.get_by_id(int(user_id))

    # TODO: Make more general
    def set_secure_cookie(self, name, val):
        self.response.set_cookie(
            'sess',
            '%s|%s' % (name, val),
            path='/'
        )

    def read_secure_cookie(self, name):
        cookie = self.request.cookies.get(name)
        if cookie:
            val, digest = cookie.split('|')
            if auth.check_secure_val(val, digest):
                return val

    def log_user_in(self, user_id):
        self.set_secure_cookie(user_id, auth.make_secure_val(user_id))
