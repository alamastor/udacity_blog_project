from handlers import Handler
from models import Post, User
import auth


class HomePage(Handler):

    def get(self):
        posts = Post.query().fetch(10)
        posts.sort(key=lambda p: p.datetime, reverse=True)
        self.render('home_page.html', posts=posts)


class PostPage(Handler):

    def get(self, post_id):
        post = Post.get_by_id(int(post_id))
        if post:
            self.render('post.html', post=post)


class LoginPage(Handler):

    def get(self):
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
            self.redirect('/')
        else:
            self.render('login.html', error=True)
