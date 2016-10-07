from base import BaseHandler


class WelcomePage(BaseHandler):

    @BaseHandler.login_required()
    def get(self):
        after_login_link = self.request.cookies.get('after_login')
        self.render(
            'welcome.html', user=self.user, after_login=after_login_link
        )
        self.delete_cookie('after_login')
