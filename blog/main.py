import webapp2

from views import HomePage, PostPage

ROUTER = [
    ('/', HomePage),
    ('/post/(\d+)', PostPage),
]

app = webapp2.WSGIApplication(ROUTER)
