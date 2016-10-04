from base import BaseHandler


class WelcomePage(BaseHandler):

    def get(self):
        if self.user:
            after_login_link = self.request.cookies.get('after_login')
            self.render('welcome.html', user=self.user, after_login=after_login_link)
        else:
            self.redirect('/login')
