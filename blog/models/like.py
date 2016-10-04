from google.appengine.ext import ndb

from blog_post import blog_key, BlogPost


class Like(ndb.Model):
    user_id = ndb.IntegerProperty(required=True)

    @classmethod
    def get_by_blog_post_id(cls, blog_post_id):
        blog_post = BlogPost.get_by_id(blog_post_id, parent=blog_key())
        return cls.query(ancestor=blog_post.key).fetch()

    @classmethod
    def get_by_blog_post_id_and_user_id(cls, blog_post_id, user_id):
        blog_post = BlogPost.get_by_id(blog_post_id, parent=blog_key())
        return cls.query(cls.user_id==user_id, ancestor=blog_post.key).fetch()[0]
