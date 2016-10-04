import re
from datetime import datetime

from base import BaseHandler
from models.like import Like
from models.comment import Comment
from models.blog_post import blog_key, BlogPost


class BlogPostPage(BaseHandler):
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

    @BaseHandler.login_required()
    def post(self, post_id=None):
        if post_id:
            self.post_id = int(post_id)
        else:
            self.post_id = None

        if self.request.get('delete'):
            self.handle_delete_request()
        elif self.request.get('like'):
            self.handle_like_request()
        elif self.post_id:
            self.update_blog_post()
        else:
            self.create_blog_post()

    def get_post(self):
        if self.post_id:
            post = BlogPost.get_by_id(self.post_id, parent=blog_key())

            if not post:
                self.abort(404)
        else:
            post = None

        return post

    def handle_delete_request(self):
        if self.request.get('delete') != 'delete':
            self.abort(400)
        self.delete()

    def handle_like_request(self):
        like_req = self.request.get('like')
        if like_req == 'like':
            self.like()
        elif like_req == 'unlike':
            self.unlike()
        else:
            self.abort(400)

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

    def delete(self):
        post = self.get_post()
        if post.user_id != self.user.key.id():
            self.abort(403)

        post.key.delete()
        self.redirect('/')

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
