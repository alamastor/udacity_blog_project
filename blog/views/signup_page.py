import re

from base import BaseHandler
from utils import auth


class SignUpPage(BaseHandler):
    USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
    PW_RE = re.compile(r'^.{3,20}$')
    EMAIL_RE = re.compile(r'^[\S]+@[\S]+.[\S]+$')

    def get(self):
        self.render('signup.html')

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')

        errors = []
        if not self.USER_RE.match(username):
            errors.append('Invalid username')
        if not self.PW_RE.match(password):
            errors.append('Invalid password')
        if password != verify:
            errors.append("Passwords didn't match")
        if email and not self.EMAIL_RE.match(email):
            errors.append('Invalid email address')

        if errors:
            self.render(
                'signup.html', username=username, email=email, errors=errors
            )
        else:
            try:
                user_id = auth.create_user(username, password, email)
            except:
                self.render(
                    'signup.html',
                    username=username,
                    email=email,
                    errors=['Username is already taken']
                )
            else:
                self.log_user_in(user_id)
                redirect_cookie = self.request.cookies.get('after_login')
                self.redirect('/welcome')
