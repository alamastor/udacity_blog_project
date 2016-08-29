import webapp2

from views import HomePage, PostPage, LoginPage, SignUpPage, CreatePage

ROUTER = [
    ('/', HomePage),
    ('/post/(\d+)', PostPage),
    ('/login', LoginPage),
    ('/signup', SignUpPage),
    ('/create', CreatePage),
]

app = webapp2.WSGIApplication(ROUTER)
