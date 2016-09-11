from datetime import datetime

import re

from handlers import Handler, AuthHandler
from models import blog_key, BlogPost, User, Comment
import auth


class HomePage(Handler, AuthHandler):

    def get(self):
        posts = BlogPost.query(ancestor=blog_key()).fetch(10)
        posts.sort(key=lambda p: p.datetime, reverse=True)
        self.render('home_page.html', user=self.user, posts=posts)


class BlogPostPage(Handler, AuthHandler):
    TITLE_RE = re.compile(r'^.{4,80}')
    CONTENT_RE = re.compile(r'^[\S\s]{4,}')

    def get(self, post_id):
        post_id = int(post_id)
        post = BlogPost.get_by_id(post_id, parent=blog_key())

        if post:
            comments = Comment.get_by_post_key(post.key)
            comments.sort(key=lambda x: x.datetime)
            self.render(
                'post.html', user=self.user, post=post, comments=comments
            )
        else:
            self.abort(404)

    def post(self, post_id=None):
        if not self.user:
            self.abort(401)

        if post_id:
            self.post_id = int(post_id)
        else:
            self.post_id = None

        if self.request.get('delete') == 'delete':
            self.delete()
        else:
            self.create_or_update()


    def get_post(self):
        if self.post_id:
            post = BlogPost.get_by_id(self.post_id, parent=blog_key())

            if not post:
                self.abort(404)
            if post.user_id != self.user.key.id():
                self.abort(401)
        else:
            post = None

        return post


    def delete(self):
        self.get_post().key.delete()
        self.redirect('/')


    def create_or_update(self):
        post = self.get_post()
        title = self.request.get('title')
        content = self.request.get('content')

        errors = []
        if not self.TITLE_RE.match(title):
            errors.append('Invalid title')
        if not self.CONTENT_RE.match(content):
            errors.append('Invalid content')

        if not errors:
            if post:
                post.title = title
                post.content = content
            else:
                post = BlogPost(
                    parent=blog_key(),
                    title=title,
                    content=content,
                    datetime=datetime.now(),
                    user_id=self.user.key.id()
                )
            post.put()

            self.redirect('/post/%i' % post.key.id())
        else:
            self.render(
                'blog_post_create_edit.html',
                title=title,
                content=content,
                errors=errors
            )

class CreateOrEditBlogPostPage(Handler, AuthHandler):

    def get(self, post_id=None):
        if not self.user:
            self.redirect('/login')

        if post_id:
            post_id = int(post_id)
            post = BlogPost.get_by_id(post_id, parent=blog_key())
            if not post:
                self.abort(404)

            if not self.user or post.user_id != self.user.key.id():
                self.abort(401)

            title = post.title
            content = post.content
        else:
            post = None
            title = ''
            content = ''

        self.render(
            'blog_post_create_edit.html',
            post=post,
            title=title,
            content=content
        )


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


class CommentPage(Handler, AuthHandler):

    def __init__(self, *args, **kwargs):
        self._blog_post = None
        super(self.__class__, self).__init__(*args, **kwargs)

    def get(self, post_id, comment_id=None):
        self.post_id = int(post_id)
        if comment_id:
            self.comment_id = int(comment_id)
        else:
            self.comment_id = None

        if self.user:
            self.render(
                'comment.html',
                user=self.user,
                comment=self.get_comment(),
                post_id=self.post_id
            )
        else:
            self.abort(401)

    def post(self, post_id, comment_id=None):
        if self.user:
            self.post_id = int(post_id)
            if comment_id:
                self.comment_id = int(comment_id)
            else:
                self.comment_id = None


            if self.request.get('delete') == 'delete':
                self.delete()
            else:
                comment_text = self.request.get('comment')
                if comment_text:
                    self.create_or_update_comment(comment_text)
                    self.redirect('/post/%i' % self.post_id)
                else:
                    error = 'Comment cannot be empty.'
                    self.render(
                        'comment.html',
                        user=self.user,
                        comment=comment_text,
                        error=error
                    )
        else:
            self.abort(401)

    def create_or_update_comment(self, comment_text):
        comment = self.get_comment()
        if comment:
            comment.comment = comment_text
            comment.datetime = datetime.now()
        else:
            comment = Comment(
                parent=self.blog_post.key,
                comment=comment_text,
                user_id=self.user.key.id(),
                datetime=datetime.now()
            )
        comment.put()

    @property
    def blog_post(self):
        if not self._blog_post:
            self._blog_post = BlogPost.get_by_id(self.post_id, parent=blog_key())
        return self._blog_post

    def get_comment(self):
        if self.comment_id:
            comment = Comment.get_by_id_and_post_key(
                self.comment_id, self.blog_post.key
            )
        else:
            comment = None

        if self.comment_id and not comment:
            self.abort(404)

        if comment and comment.user_id != self.user.key.id():
            self.abort(401)

        self._comment = comment

        return comment


    def delete(self):
        comment = Comment.get_by_id_and_post_key(
            self.comment_id, self.blog_post.key
        )

        if comment.user_id != self.user.key.id():
            self.abort(401)

        comment.key.delete()

        self.redirect('/post/%i' % self.post_id)
