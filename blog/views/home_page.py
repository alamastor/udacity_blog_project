from google.appengine.datastore.datastore_query import Cursor

from base import BaseHandler
from models.blog_post import BlogPost, blog_key


class HomePage(BaseHandler):
    ''' Handler for displaying home page, paginated with links to ten
    blog posts per page.
    '''
    def get(self):
        ''' Return response with home page rendered.
        '''
        # Get datastor cursor from query params, used to determine current
        # page.
        cur = Cursor(urlsafe=self.request.get('cur'))
        q = BlogPost.query(ancestor=blog_key())
        q = q.order(-BlogPost.datetime)

        # Google Datastore api call, fetching next ten entries, based on
        # cursor value.
        posts, next_cursor, more = q.fetch_page(10, start_cursor=cur)
        self.render(
            'home_page.html',
            user=self.user,
            posts=posts,
            cur=next_cursor,
            show_next_page=more,
        )
