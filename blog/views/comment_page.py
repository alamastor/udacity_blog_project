from datetime import datetime

from base import BaseHandler
from models.comment import Comment
from models.blog_post import blog_key, BlogPost


class CommentPage(BaseHandler):
    ''' Handler responsible for rendering comment edit page, editing,
    updating and deleting comments.
    '''

    def __init__(self, request, response):
        super(CommentPage, self).__init__(request, response)
        # Property method caches.
        self._blog_post = None
        self._comment = None

    @BaseHandler.login_required(abort=401)
    def get(self, post_id, comment_id=None):
        ''' Return response with comment create/edit page.
        '''
        self.post_id = int(post_id)
        if comment_id:
            self.comment_id = int(comment_id)
        else:
            self.comment_id = None

        self.render(
            'comment.html',
            user=self.user,
            comment=self.comment,
            post_id=self.post_id
        )

    @BaseHandler.login_required(abort=401)
    def post(self, post_id, comment_id=None):
        ''' Update, create or delete a comment.
        '''
        self.post_id = int(post_id)
        if comment_id:
            self.comment_id = int(comment_id)
        else:
            self.comment_id = None

        if self.request.get('delete'):
            self.handle_delete_request()
        else:
            comment_text = self.request.get('comment')
            if comment_text:
                self.create_or_update_comment(comment_text)
                self.redirect('/post/%i' % self.post_id)
            else:
                self.render_error('Comment cannot be empty.')

    def handle_delete_request(self):
        ''' Delete comment and redirect to post.
        '''
        if self.request.get('delete') != 'delete':
            self.abort(400)
        self.delete()
        self.redirect('/post/%i' % self.post_id)

    def create_or_update_comment(self, comment_text):
        ''' Create comment, or update if it already exists.
        '''
        if self.comment:
            self.comment.comment = comment_text
            self.comment.datetime = datetime.now()
        else:
            self.comment = Comment(
                parent=self.blog_post.key,
                comment=comment_text,
                user_id=self.user.key.id(),
                datetime=datetime.now()
            )
        self.comment.put()

    @property
    def blog_post(self):
        ''' Return blog post model this comment relates to.
        '''
        if not self._blog_post:
            self._blog_post = BlogPost.get_by_id(
                self.post_id, parent=blog_key()
            )
        return self._blog_post

    @property
    def comment(self):
        ''' Return comment model.
        '''
        if not self._comment:
            if self.comment_id:
                comment = Comment.get_by_id_and_blog_post_key(
                    self.comment_id, self.blog_post.key
                )
            else:
                comment = None

            if self.comment_id and not comment:
                self.abort(404)

            if comment and comment.user_id != self.user.key.id():
                self.abort(403)

            self._comment = comment
        return self._comment

    @comment.setter
    def comment(self, value):
        self._comment = value

    def delete(self):
        ''' Delete comment.
        '''
        if self.comment.user_id != self.user.key.id():
            self.abort(403)

        self.comment.key.delete()

    def render_error(self, error):
        ''' Render page with error message.
        '''
        self.render(
            'comment.html',
            user=self.user,
            comment='',
            error=error
        )
