import webapp2

from views import HomePage, PostPage, LoginPage

ROUTER = [
    ('/', HomePage),
    ('/post/(\d+)', PostPage),
    ('/login', LoginPage),
]

app = webapp2.WSGIApplication(ROUTER)
