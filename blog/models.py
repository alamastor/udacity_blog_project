from google.appengine.ext import ndb
import re


# Key to use as parent for all blog post to ensure strong-consistancy.
# This means changes to to BlogPost will be limited to 1/second, if
# greater than this was require stop using the key and don't rely on
# strong consistancy.
def blog_key():
    return ndb.Key('Blog', 'DEFAULT_BLOG')


class BlogPost(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)

    @property
    def full_key(self):
        return ndb.Key(BlogPost, self.key.id(), parent=blog_key())

    @property
    def date_str(self):
        return self.datetime.strftime('%-d-%b-%Y')

    @property
    def formatted_content(self):
        return self.content.replace('\n', '<br>')

    @property
    def username(self):
        return User.get_by_id(self.user_id).username

    @property
    def paragraphs(self):
        return self.content.split('\n')

class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)
    email = ndb.StringProperty()

    @classmethod
    def get_by_username(cls, username):
        ''' Return one user object of username username.'''
        users = cls.query(cls.username==username).fetch()
        if users:
            if len(users) != 1:
                msg = 'User %s appears %s times in db' % (username, len(users))
                raise RuntimeError(msg)
            return users[0]


class Comment(ndb.Model):
    comment = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)

    @classmethod
    def get_by_post_key(cls, parent_key):
        return cls.query(ancestor=parent_key).fetch()

    @classmethod
    def get_by_id_and_post_key(cls, comment_id, post_key):
        return cls.get_by_id(comment_id, parent=post_key)

    @property
    def formatted_date(self):
        return self.datetime.strftime('%-d-%b-%Y')

    @property
    def paragraphs(self):
        return self.comment.split('\n')


class Like(ndb.Model):
    user_id = ndb.IntegerProperty(required=True)

    @classmethod
    def get_by_blog_post_id(cls, blog_post_id):
        blog_post = BlogPost.get_by_id(blog_post_id, parent=blog_key())
        return cls.query(ancestor=blog_post.key).fetch()
