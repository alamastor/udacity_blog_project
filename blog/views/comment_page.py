from datetime import datetime

from base import Handler, AuthHandler
from models.models import blog_key, Comment, BlogPost


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
