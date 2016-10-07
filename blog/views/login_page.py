from base import BaseHandler
from models.user import User
from utils import auth


class LoginPage(BaseHandler):
    ''' Handler responsible for rendering login page and loging a
    user in.
    '''

    def get(self):
        ''' Return respose with login page.
        '''
        # Redirect cookie provides an address to return the user back
        # to after logint.
        redirect_cookie = self.request.cookies.get('after_login')
        if not redirect_cookie and self.request.referer:
            # If redirect cookie was not set set it now to page referer.
            self.set_cookie('after_login', self.request.referer)
        self.render('login.html')

    def post(self):
        ''' Validate user login input and login if ok, otherwise
        display errors.
        '''
        username = self.request.get('username')
        password = self.request.get('password')

        user = User.get_by_username(username)

        valid_user = False
        if user:
            pw_hash = auth.make_pw_hash(username, password, user.salt)
            if auth.constant_time_compare(user.pw_hash, pw_hash):
                valid_user = True

        if valid_user:
            self.log_user_in(user.key.id())
            self.redirect('/welcome')
        else:
            self.render('login.html', error=True)
