from google.appengine.ext import ndb


class Post(ndb.Model):
    title = ndb.StringProperty(required=True)
    content = ndb.TextProperty(required=True)
    datetime = ndb.DateTimeProperty(required=True)

    @property
    def date_str(self):
        return self.datetime.strftime('%d-%b-%Y')

    @property
    def formatted_content(self):
        return self.content.replace('\n', '<br>')


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
    def get_by_id_and_post_id(cls, comment_id, post_id):
        return cls.get_by_id(comment_id, parent=ndb.Key(Post, post_id))

    @property
    def formatted_date(self):
        return self.datetime.strftime('%-d-%b-%Y')
