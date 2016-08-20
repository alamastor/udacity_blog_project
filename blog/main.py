import os

import webapp2
import jinja2


template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(template_dir),
    autoescape=True
)


class HomePage(webapp2.RequestHandler):

    def get(self):
        self.response.write(jinja_env.get_template('home_page.html').render())

ROUTER = [
    ('/', HomePage),
]

app = webapp2.WSGIApplication(ROUTER)
