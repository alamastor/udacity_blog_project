import webapp2

from views import (
    HomePage, PostPage, LoginPage, SignUpPage, CreatePage, CommentPage
)

ROUTER = [
    ('/', HomePage),
    ('/post/(\d+)', PostPage),
    ('/post/(\d+)/comment', CommentPage),
    ('/post/(\d+)/comment/(\d+)', CommentPage),
    ('/login', LoginPage),
    ('/signup', SignUpPage),
    ('/create', CreatePage),
]

app = webapp2.WSGIApplication(ROUTER)
