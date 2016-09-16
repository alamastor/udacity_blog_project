import webapp2

from views import (
    HomePage, BlogPostPage, LoginPage, SignUpPage, CommentPage,
    CreateOrEditBlogPostPage, LogoutHandler
)

ROUTER = [
    ('/', HomePage),
    ('/post', BlogPostPage),
    ('/post/(\d+)', BlogPostPage),
    ('/post/(\d+)/edit', CreateOrEditBlogPostPage),
    ('/post/create', CreateOrEditBlogPostPage),
    ('/post/(\d+)/comment', CommentPage),
    ('/post/(\d+)/comment/(\d+)', CommentPage),
    ('/login', LoginPage),
    ('/signup', SignUpPage),
    ('/logout', LogoutHandler),
]

app = webapp2.WSGIApplication(ROUTER)
