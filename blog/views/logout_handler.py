import webapp2


class LogoutHandler(webapp2.RequestHandler):

    def post(self):
        self.response.delete_cookie('sess')
        if self.request.referer:
            self.redirect(self.request.referer)
        else:
            self.redirect('/')
