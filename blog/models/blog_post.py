from google.appengine.ext import ndb

from user import User


def blog_key():
    ''' Key to use as parent for all blog posts to ensure strong-consistancy.
    This means changes to to BlogPost will be limited to 1/second, if
    greater than this was require stop using the key and don't rely on
    strong consistancy.
    '''
    return ndb.Key('Blog', 'DEFAULT_BLOG')


class BlogPost(ndb.Model):
    ''' Model representing a blog post.
    '''
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)
    user_id = ndb.IntegerProperty(required=True)

    @property
    def full_key(self):
        ''' Return key with from model key and parent key. This will
        generally used instead of the model key.
        '''
        return ndb.Key(BlogPost, self.key.id(), parent=blog_key())

    @property
    def date_str(self):
        ''' Return stringified version of blog post date.
        '''
        return self.datetime.strftime('%-d-%b-%Y')

    @property
    def username(self):
        ''' Return username of blog post creator.
        '''
        return User.get_by_id(self.user_id).username

    @property
    def paragraphs(self):
        ''' Return a list of paragraphs from content.
        '''
        return self.content.split('\n')
