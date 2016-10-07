import webapp2

from views.base import BaseHandler

class LogoutHandler(BaseHandler):

    def post(self):
        self.delete_cookie('sess')
        if self.request.referer:
            self.redirect(self.request.referer)
        else:
            self.redirect('/')
