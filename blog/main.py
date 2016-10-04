import webapp2

from views.home_page import HomePage
from views.blog_post_page import BlogPostPage
from views.create_edit_page import CreateOrEditBlogPostPage
from views.login_page import LoginPage
from views.signup_page import SignUpPage
from views.welcome_page import WelcomePage
from views.comment_page import CommentPage
from views.logout_handler import LogoutHandler


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
