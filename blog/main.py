import webapp2

from views import HomePage, PostPage, LoginPage, SignUpPage

ROUTER = [
    ('/', HomePage),
    ('/post/(\d+)', PostPage),
    ('/login', LoginPage),
    ('/signup', SignUpPage),
]

app = webapp2.WSGIApplication(ROUTER)
