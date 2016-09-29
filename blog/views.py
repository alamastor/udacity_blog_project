from datetime import datetime
import re

import webapp2
from google.appengine.datastore.datastore_query import Cursor

from handlers import Handler, AuthHandler
from models import blog_key, BlogPost, User, Comment, Like
import auth


class HomePage(Handler, AuthHandler):

    def get(self):
        cur = Cursor(urlsafe=self.request.get('cur'))
        q = BlogPost.query(ancestor=blog_key())
        q = q.order(-BlogPost.datetime)

        posts, next_cursor, more = q.fetch_page(10, start_cursor=cur)
        self.render(
            'home_page.html',
            user=self.user,
            posts=posts,
            cur=next_cursor,
            show_next_page=more,
        )


class BlogPostPage(Handler, AuthHandler):
    TITLE_RE = re.compile(r'^.{4,80}')
    CONTENT_RE = re.compile(r'^[\S\s]{4,}')

    def get(self, post_id):
        self.post_id = int(post_id)
        self.render_blog_post()

    def render_blog_post(self):
        post = BlogPost.get_by_id(self.post_id, parent=blog_key())

        if post:
            comments = Comment.get_by_post_key(post.key)
            comments.sort(key=lambda x: x.datetime)
            self.render(
                'post.html',
                user=self.user,
                post=post,
                comments=comments,
                already_liked=self.already_liked_blog_post,
                is_creator=self.is_blog_post_creator,
                likes=self.likes
            )
        else:
            self.abort(404)

    def post(self, post_id=None):
        if self.user:
            if post_id:
                self.post_id = int(post_id)
            else:
                self.post_id = None

            delete_req = self.request.get('delete')
            like_req = self.request.get('like')

            if delete_req:
                if delete_req == 'delete':
                    self.delete()
                else:
                    self.abort(400)
            elif like_req:
                if like_req == 'like':
                    self.like()
                elif like_req == 'unlike':
                    self.unlike()
                else:
                    self.abort(400)
            elif self.post_id:
                self.update_blog_post()
            else:
                self.create_blog_post()
        else:
            self.redirect('/login')

    def get_post(self):
        if self.post_id:
            post = BlogPost.get_by_id(self.post_id, parent=blog_key())

            if not post:
                self.abort(404)
        else:
            post = None

        return post

    def delete(self):
        post = self.get_post()
        if post.user_id != self.user.key.id():
            self.abort(403)

        post.key.delete()
        self.redirect('/')

    def create_blog_post(self):
        title = self.request.get('title')
        content = self.request.get('content')

        errors = self.blog_post_validation_errors(title, content)
        if errors:
            self.render_post_validation_errors(title, content, errors)
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

    def update_blog_post(self):
        post = self.get_post()
        if post.user_id != self.user.key.id():
            self.abort(403)

        title = self.request.get('title')
        content = self.request.get('content')

        errors = self.blog_post_validation_errors(title, content)
        if errors:
            self.render_post_validation_errors(title, content, errors)
        else:
            post.title = title
            post.content = content
            post.put()

            self.redirect('/post/%i' % post.key.id())

    def blog_post_validation_errors(self, title, content):
        errors = []
        if not self.TITLE_RE.match(title):
            errors.append('Invalid title')
        if not self.CONTENT_RE.match(content):
            errors.append('Invalid content')
        return errors

    def render_post_validation_errors(self, title, content, errors):
        self.render(
            'blog_post_create_edit.html',
            title=title,
            content=content,
            errors=errors
        )

    @property
    def is_blog_post_creator(self):
        if self.user and self.user.key.id() == self.get_post().user_id:
            return True
        else:
            return False

    def like(self):
        if self.is_blog_post_creator:
            self.abort(403)

        if self.already_liked_blog_post:
            self.abort(403)

        Like(parent=self.get_post().key, user_id=self.user.key.id()).put()

        self.render_blog_post()

    def unlike(self):
        if self.is_blog_post_creator:
            self.abort(403)

        if not self.already_liked_blog_post:
            self.abort(403)

        like = Like.get_by_blog_post_id_and_user_id(
            self.get_post().key.id(), self.user.key.id()
        )
        like.key.delete()

        self.render_blog_post()


    @property
    def already_liked_blog_post(self):
        likes = Like.get_by_blog_post_id(self.post_id)
        if self.user and self.user.key.id() in [l.user_id for l in likes]:
            return True
        else:
            return False

    @property
    def likes(self):
        return len(Like.get_by_blog_post_id(self.post_id))


class CreateOrEditBlogPostPage(Handler, AuthHandler):

    def get(self, post_id=None):
        if self.user:
            if post_id:
                post_id = int(post_id)
                post = BlogPost.get_by_id(post_id, parent=blog_key())
                if not post:
                    self.abort(404)

                if post.user_id != self.user.key.id():
                    self.abort(403)

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
                content=content,
                user=self.user
            )
        else:
            self.redirect_to_login()


class LoginPage(Handler, AuthHandler):

    def get(self):
        redirect_cookie = self.request.cookies.get('after_login')
        if not redirect_cookie and self.request.referer:
            self.set_cookie('after_login', self.request.referer)
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
            self.redirect('/welcome')
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
        if email and not self.EMAIL_RE.match(email):
            errors.append('Invalid email address')

        if errors:
            self.render(
                'signup.html', username=username, email=email, errors=errors
            )
        else:
            user_id = auth.create_user(username, password, email)
            self.log_user_in(user_id)
            redirect_cookie = self.request.cookies.get('after_login')
            self.redirect('/welcome')


class WelcomePage(Handler, AuthHandler):

    def get(self):
        if self.user:
            after_login_link = self.request.cookies.get('after_login')
            self.render('welcome.html', user=self.user, after_login=after_login_link)
        else:
            self.redirect('/login')


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
            self.abort(403)

        self._comment = comment

        return comment


    def delete(self):
        comment = Comment.get_by_id_and_post_key(
            self.comment_id, self.blog_post.key
        )

        if comment.user_id != self.user.key.id():
            self.abort(403)

        comment.key.delete()

        self.redirect('/post/%i' % self.post_id)


class LogoutHandler(webapp2.RequestHandler):

    def post(self):
        self.response.delete_cookie('sess')
        if self.request.referer:
            self.redirect(self.request.referer)
        else:
            self.redirect('/')
