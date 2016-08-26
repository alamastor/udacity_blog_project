import re

from handlers import Handler, AuthHandler
from models import Post, User
import auth


class HomePage(Handler, AuthHandler):

    def get(self):
        posts = Post.query().fetch(10)
        posts.sort(key=lambda p: p.datetime, reverse=True)
        self.render('home_page.html', user=self.user, posts=posts)


class PostPage(Handler):

    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if post:
            self.render('post.html', post=post)


class LoginPage(Handler, AuthHandler):

    def get(self):
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.get_by_username(username)

        valid_user = False
        if user:
            pw_hash = auth.make_pw_hash(username, password, user.salt)
            if user.pw_hash == pw_hash:
                valid_user = True

        if valid_user:
            self.log_user_in(user.key.id())
            self.redirect('/')
        else:
            self.render('login.html', error=True)


class SignUpPage(Handler):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PW_RE = re.compile(r"^.{3,20}$")
    EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")

    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = []
        if not self.USER_RE.match(username):
            errors.append('Invalid username')
        if not self.PW_RE.match(password):
            errors.append('Invalid password')
        if password != verify:
            errors.append("Passwords didn't match")
        if not self.EMAIL_RE.match(email):
            errors.append('Invalid email')

        if errors:
            self.render(
                'signup.html', username=username, email=email, errors=errors
            )
        else:
            self.redirect('/')
