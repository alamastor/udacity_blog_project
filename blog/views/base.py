from functools import wraps
import os

import webapp2
import jinja2

from utils import auth
from models.user import User


template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
)


class BaseHandler(webapp2.RequestHandler):
    ''' Base request handler class, other handlers should inherit from this.
    '''

    def __init__(self, request, response):
        self.initialize(request, response)
        # Set user from cookie if present.
        user_id = self.read_secure_cookie('sess')
        self.user = user_id and User.get_by_id(int(user_id))

    def render_str(self, template, **kwargs):
        ''' Render a jinja2 template as html string.
        '''
        t = jinja_env.get_template(template)
        return t.render(kwargs)

    def render(self, template, **kwargs):
        ''' Write a jinja2 template to the HTTP response.
        '''
        self.response.write(self.render_str(template, **kwargs))

    def set_cookie(self, name, val):
        ''' Set a cookie in the HTTP response.
        '''
        self.response.set_cookie(name, val, path='/')

    def set_secure_cookie(self, name, val):
        ''' Set a cookie in the HTTP response with with secure hash attached.
        '''
        secured_val = '%s|%s' % (val, auth.make_secure_val(val))
        self.response.set_cookie(name, secured_val, path='/')

    def read_secure_cookie(self, name):
        ''' Read a cookie from a HTTP request with secure hash attached.
        '''
        cookie = self.request.cookies.get(name)
        if cookie:
            val, digest = cookie.split('|')
            if auth.check_secure_val(val, digest):
                return val

    def delete_cookie(self, name):
        self.response.delete_cookie(name)

    def log_user_in(self, user_id):
        ''' Log a user in by setting session cookie.
        '''
        self.set_secure_cookie('sess', user_id)

    def redirect_to_login(self):
        ''' Set HTTP response to redirect to login page, and set a cookie
        that will cause login page to redirect back to current page after
        login.
        '''
        self.set_cookie('after_login', self.request.url)
        self.redirect('/login')

    @staticmethod
    def login_required(abort=None):
        ''' Decorator method for adding automatic handling of logged out users
        to handler methods.

        Will redirect to login page if called with no arguments, eg:
        @login_required()
        def get(self):
            pass

        Will abort with passed HTTP code if called with abort argument, eg:
        @login_required(abort=401)
        def get(self):
            pass
        '''
        def login_required_decorator(method):
            @wraps(method)
            def wrapped_method(self, *args, **kwargs):
                if not self.user:
                    if abort:
                        self.abort(abort)
                    else:
                        self.redirect_to_login()
                else:
                    return method(self, *args, **kwargs)
            return wrapped_method
        return login_required_decorator
