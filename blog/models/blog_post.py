from google.appengine.ext import ndb

from user import User


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
