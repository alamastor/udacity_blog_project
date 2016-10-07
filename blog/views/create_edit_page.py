from base import BaseHandler
from models.blog_post import blog_key, BlogPost


class CreateOrEditBlogPostPage(BaseHandler):

    @BaseHandler.login_required()
    def get(self, post_id=None):
        ''' Handler responsible for rendering the blog post create/edit page.
        Forms on this page post to the BlogPostPage handler.
        '''
        if post_id:
            # Recieved post id, so user is editing blog post.
            post_id = int(post_id)
            post = BlogPost.get_by_id(post_id, parent=blog_key())
            if not post:
                self.abort(404)

            if post.user_id != self.user.key.id():
                self.abort(403)

            title = post.title
            content = post.content
        else:
            # Did not recieved post user is creating a new blog post.
            post = None
            title = ''
            content = ''
        errors = []

        if self.request.get_all('error'):
            # Received error in query params, render page with validations
            # error/s and previously entered content.
            title = self.request.get('title')
            content = self.request.get('content')
            errors = self.request.get_all('error')

        self.render(
            'blog_post_create_edit.html',
            post=post,
            title=title,
            content=content,
            user=self.user,
            errors=errors,
            referer=self.request.referer or '/'
        )
