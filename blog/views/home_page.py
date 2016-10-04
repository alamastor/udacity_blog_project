from google.appengine.datastore.datastore_query import Cursor

from base import Handler, AuthHandler
from models.blog_post import blog_key, BlogPost


class HomePage(Handler, AuthHandler):

    def get(self):
        cur = Cursor(urlsafe=self.request.get('cur'))
        q = BlogPost.query(ancestor=blog_key())
        q = q.order(-BlogPost.datetime)

        posts, next_cursor, more = q.fetch_page(10, start_cursor=cur)
        self.render(
            'home_page.html',
            user=self.user,
            posts=posts,
            cur=next_cursor,
            show_next_page=more,
        )
