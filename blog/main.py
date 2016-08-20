import webapp2

from views import HomePage

ROUTER = [
    ('/', HomePage),
]

app = webapp2.WSGIApplication(ROUTER)
