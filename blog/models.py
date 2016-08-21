from google.appengine.ext import ndb


class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)


class User(ndb.Model):
    username = ndb.StringProperty(required=True)
    pw_hash = ndb.StringProperty(required=True)
    salt = ndb.StringProperty(required=True)

    @classmethod
    def get_by_username(cls, username):
        ''' Return one user object of username username.'''
        users = cls.query(cls.username==username).fetch()
        if users:
            if len(users) != 1:
                msg = 'User %s appears %s times in db' % (username, len(users))
                raise RuntimeError(msg)
            return users[0]
