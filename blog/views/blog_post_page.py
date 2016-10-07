import re
from datetime import datetime

from base import BaseHandler
from models.like import Like
from models.comment import Comment
from models.blog_post import blog_key, BlogPost


class BlogPostPage(BaseHandler):
    ''' Handler responsible for rendering, creating, editing, deleting,
    commenting on and liking blog posts.
    '''
    TITLE_RE = re.compile(r'^.{4,80}')
    CONTENT_RE = re.compile(r'^[\S\s]{4,}')

    def __init__(self, request, response):
        super(BlogPostPage, self).__init__(request, response)
        # Property method caches.
        self._blog_post = None

    def get(self, blog_post_id):
        ''' Return response with full blog post, comments and likes.
        '''
        self.blog_post_id = int(blog_post_id)
        self.render_blog_post()

    @BaseHandler.login_required()
    def post(self, blog_post_id=None):
        ''' Posts with delete or like values will trigger those actions
        otherwise a create or update will be attempted. If the post url
        contained a blog post id and update will be attempted and a new id will
        be created.
        '''
        if blog_post_id:
            self.blog_post_id = int(blog_post_id)
        else:
            self.blog_post_id = None

        if self.request.get('delete'):
            self.handle_delete_request()
        elif self.request.get('like'):
            self.handle_like_request()
        elif self.blog_post_id:
            # If post had a blog post id then update the blog post,
            # otherwise, create a new blog post.
            self.update_blog_post()
        else:
            self.create_blog_post()

    def render_blog_post(self):
        ''' Return HTTP response with rendered blog post.
        '''
        comments = Comment.get_by_blog_post_key(self.blog_post.key)
        comments.sort(key=lambda x: x.datetime)
        self.render(
            'blog_post.html',
            user=self.user,
            blog_post=self.blog_post,
            comments=comments,
            already_liked=self.already_liked_blog_post,
            is_creator=self.is_blog_post_creator,
            likes=self.likes
        )

    @property
    def blog_post(self):
        ''' Get blog post model object from id, will return None if id is None.
        '''
        if not self._blog_post:
            if self.blog_post_id:
                blog_post = BlogPost.get_by_id(
                    self.blog_post_id, parent=blog_key()
                )

                if not blog_post:
                    self.abort(404)
                self._blog_post = blog_post
        return self._blog_post

    def handle_delete_request(self):
        ''' Delete blog post if the delete post had value delete.
        '''
        if self.request.get('delete') != 'delete':
            self.abort(400)
        self.delete()
        self.redirect('/')

    def handle_like_request(self):
        ''' Like or unlike a blog post depending on the value of like post.
        '''
        like_req = self.request.get('like')
        if like_req == 'like':
            self.like()
        elif like_req == 'unlike':
            self.unlike()
        else:
            self.abort(400)
        self.render_blog_post()

    def create_blog_post(self):
        ''' Create a blog post from request title and content. Will render
        page with validation errors if validation fails.
        '''
        title = self.request.get('title')
        content = self.request.get('content')

        errors = self.blog_post_validation_errors(title, content)
        if errors:
            self.redirect_with_errors(title, content, errors)
        else:
            blog_post = BlogPost(
                parent=blog_key(),
                title=title,
                content=content,
                datetime=datetime.now(),
                user_id=self.user.key.id()
            )
            blog_post.put()

            self.redirect('/post/%i' % blog_post.key.id())

    def update_blog_post(self):
        ''' Update the blog post from request title and content. Will render
        page with validation errors if validation fails.
        '''
        blog_post = self.blog_post
        if blog_post.user_id != self.user.key.id():
            self.abort(403)

        title = self.request.get('title')
        content = self.request.get('content')

        errors = self.blog_post_validation_errors(title, content)
        if errors:
            self.redirect_with_errors(title, content, errors)
        else:
            blog_post.title = title
            blog_post.content = content
            blog_post.put()

            self.redirect('/post/%i' % blog_post.key.id())

    def blog_post_validation_errors(self, title, content):
        ''' Validate post request for errors for creating or updating a
        blog post, returning a list of strings describing the errors.
        '''
        errors = []
        if not self.TITLE_RE.match(title):
            errors.append('Invalid title')
        if not self.CONTENT_RE.match(content):
            errors.append('Invalid content')
        return errors

    def redirect_with_errors(self, title, content, errors):
        ''' Redirect to back to create/edit page after invalid post.
        '''
        if self.blog_post_id:
            url_string = '/post/%i/edit?' % self.blog_post_id
        else:
            url_string = '/post/create?'
        url_string += 'title=' + title
        url_string += '&content=' + content
        for error in errors:
            url_string += '&error=' + error
        self.redirect(url_string)

    @property
    def is_blog_post_creator(self):
        ''' Is current user creator of blog post.
        '''
        if self.user and self.user.key.id() == self.blog_post.user_id:
            return True
        else:
            return False

    def delete(self):
        ''' Delete the blog post.
        '''
        if not self.is_blog_post_creator:
            self.abort(403)
        self.blog_post.key.delete()

    def like(self):
        ''' Like blog post.
        '''
        if self.is_blog_post_creator:
            self.abort(403)

        if self.already_liked_blog_post:
            self.abort(403)

        Like(parent=self.blog_post.key, user_id=self.user.key.id()).put()

    def unlike(self):
        ''' Unlike blog post.
        '''
        if self.is_blog_post_creator:
            self.abort(403)

        if not self.already_liked_blog_post:
            self.abort(403)

        like = Like.get_by_blog_post_id_and_user_id(
            self.blog_post.key.id(), self.user.key.id()
        )
        like.key.delete()

    @property
    def already_liked_blog_post(self):
        ''' Has current user already like the post.
        '''
        likes = Like.get_by_blog_post_id(self.blog_post_id)
        if self.user and self.user.key.id() in [l.user_id for l in likes]:
            return True
        else:
            return False

    @property
    def likes(self):
        ''' Number of likes post currently has.
        '''
        return len(Like.get_by_blog_post_id(self.blog_post_id))
