from handlers import Handler
from models import Post


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
