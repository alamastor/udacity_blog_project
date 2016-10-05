from google.appengine.ext import ndb

from user import User


class Comment(ndb.Model):
    comment = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)

    @classmethod
    def get_by_blog_post_key(cls, parent_key):
        return cls.query(ancestor=parent_key).fetch()

    @classmethod
    def get_by_id_and_blog_post_key(cls, comment_id, post_key):
        return cls.get_by_id(comment_id, parent=post_key)

    @property
    def formatted_date(self):
        return self.datetime.strftime('%-d-%b-%Y')

    @property
    def paragraphs(self):
        return self.comment.split('\n')

    @property
    def username(self):
        return User.get_by_id(self.user_id).username
