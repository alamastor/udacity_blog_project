import webapp2

from views.base import BaseHandler

class LogoutHandler(BaseHandler):
    ''' Handler for logging user out.
    '''

    def post(self):
        ''' Log user out by deleting session key. Redirect back to referer
        afterwards.
        '''
        self.delete_cookie('sess')
        if self.request.referer:
            self.redirect(self.request.referer)
        else:
            self.redirect('/')
