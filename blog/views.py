from datetime import datetime

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


class SignUpPage(Handler, AuthHandler):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PW_RE = re.compile(r'^.{3,20}$')
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+.[\S]+$')

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
            errors.append('Invalid email address')

        if errors:
            self.render(
                'signup.html', username=username, email=email, errors=errors
            )
        else:
            user_id = auth.create_user(username, password, email)
            self.log_user_in(user_id)
            self.redirect('/')


class CreatePage(Handler, AuthHandler):
    TITLE_RE = re.compile(r'^.{4,80}')
    CONTENT_RE = re.compile(r'^[\S\s]{4,}')

    def get(self):
        if self.user:
            self.render('create.html')
        else:
            self.redirect('/login')

    def post(self):
        if self.user:
            title = self.request.get('title')
            content = self.request.get('content')

            errors = []
            if not self.TITLE_RE.match(title):
                errors.append('Invalid title')
            if not self.CONTENT_RE.match(content):
                errors.append('Invalid content')

            if not errors:
                post = Post(
                    title=title,
                    content=content,
                    datetime=datetime.now()
                )
                post.put()

                self.redirect('/post/' + str(post.key.id()))
            else:
                self.render('create.html', title=title, content=content, errors=errors)
        else:
            self.abort(401)
