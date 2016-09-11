import webapp2

from views import (
    HomePage, BlogPostPage, LoginPage, SignUpPage, CreatePage, CommentPage,
    EditBlogPostPage
)

ROUTER = [
    ('/', HomePage),
    ('/post/(\d+)', BlogPostPage),
    ('/post/(\d+)/edit', EditBlogPostPage),
    ('/post/(\d+)/comment', CommentPage),
    ('/post/(\d+)/comment/(\d+)', CommentPage),
    ('/login', LoginPage),
    ('/signup', SignUpPage),
    ('/create', CreatePage),
]

app = webapp2.WSGIApplication(ROUTER)
