from base import Handler, AuthHandler
from models.models import User
import auth


class LoginPage(Handler, AuthHandler):

    def get(self):
        redirect_cookie = self.request.cookies.get('after_login')
        if not redirect_cookie and self.request.referer:
            self.set_cookie('after_login', self.request.referer)
        self.render('login.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.get_by_username(username)

        valid_user = False
        if user:
            pw_hash = auth.make_pw_hash(username, password, user.salt)
            if user.pw_hash == pw_hash:
                valid_user = True

        if valid_user:
            self.log_user_in(user.key.id())
            self.redirect('/welcome')
        else:
            self.render('login.html', error=True)
