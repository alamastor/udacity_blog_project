from google.appengine.ext import ndb

from user import User


class Comment(ndb.Model):
    ''' Model representing comment on a blog post. Should be created with a blog
    post as parent.
    '''
    comment = ndb.TextProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)

    @classmethod
    def get_by_blog_post_key(cls, parent_key):
        ''' Return a list of comments, which have parent_key as a parent.
        '''
        return cls.query(ancestor=parent_key).fetch()

    @classmethod
    def get_by_id_and_blog_post_key(cls, comment_id, post_key):
        ''' Return a comment from a comment id and its parents key.
        '''
        return cls.get_by_id(comment_id, parent=post_key)

    @property
    def formatted_date(self):
        ''' Return the comment's date as a formatted string.
        '''
        return self.datetime.strftime('%-d-%b-%Y')

    @property
    def paragraphs(self):
        ''' Return a list of paragraphs from comment.
        '''
        return self.comment.split('\n')

    @property
    def username(self):
        ''' Return a the username of the creator of the comment.
        '''
        return User.get_by_id(self.user_id).username
