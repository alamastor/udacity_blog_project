from base import BaseHandler
from models.blog_post import blog_key, BlogPost


class CreateOrEditBlogPostPage(BaseHandler):

    @BaseHandler.login_required()
    def get(self, post_id=None):
        if post_id:
            post_id = int(post_id)
            post = BlogPost.get_by_id(post_id, parent=blog_key())
            if not post:
                self.abort(404)

            if post.user_id != self.user.key.id():
                self.abort(403)

            title = post.title
            content = post.content
            errors = []
        else:
            post = None
            title = ''
            content = ''
            errors = []

        if self.request.get('error', allow_multiple=True):
            title = self.request.get('title')
            content = self.request.get('content')
            errors = self.request.get('error', allow_multiple=True)

        self.render(
            'blog_post_create_edit.html',
            post=post,
            title=title,
            content=content,
            user=self.user,
            errors=errors
        )
