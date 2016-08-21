from google.appengine.ext import ndb

class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)

    @property
    def url(self):
        return '/posts/' + self.title.lower().replace(' ', '-')