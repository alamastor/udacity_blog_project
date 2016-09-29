import webapp2

from views.views import (
    HomePage, BlogPostPage, LoginPage, SignUpPage, CommentPage,
    CreateOrEditBlogPostPage, LogoutHandler, WelcomePage
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
    ('/welcome', WelcomePage),
]

app = webapp2.WSGIApplication(ROUTER)
