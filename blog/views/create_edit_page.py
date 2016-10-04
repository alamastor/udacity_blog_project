from base import Handler, AuthHandler
from models import blog_key, BlogPost


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
