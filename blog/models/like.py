from google.appengine.ext import ndb

from blog_post import blog_key, BlogPost


class Like(ndb.Model):
    ''' Model representing a like of a post. Should be create with a blog
    post as parent.
    '''
    user_id = ndb.IntegerProperty(required=True)

    @classmethod
    def get_by_blog_post_id(cls, blog_post_id):
        ''' Return a list of all likes associated with a blog post.
        '''
        blog_post = BlogPost.get_by_id(blog_post_id, parent=blog_key())
        return cls.query(ancestor=blog_post.key).fetch()

    @classmethod
    def get_by_blog_post_id_and_user_id(cls, blog_post_id, user_id):
        ''' Return the like associated with a blog post and user.
        '''
        blog_post = BlogPost.get_by_id(blog_post_id, parent=blog_key())
        query = cls.query(cls.user_id == user_id, ancestor=blog_post.key)
        return query.fetch()[0]
