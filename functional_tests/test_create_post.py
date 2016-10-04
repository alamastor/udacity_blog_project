from datetime import datetime

import base
from base import run_app, browser
from blog.utils import auth
from pages import HomePage, LoginPage, CreatePage, BlogPostPage, WelcomePage


def test_create_post(run_app, browser):
    # User visits home page and clicks link to create post
    HomePage(browser).visit_page().create_blog_post_link.click()

    # User is not logged in and gets redirected to login page.
    login_page = LoginPage(browser)

    # User logs in.
    test_user = base.create_test_user()
    login_page.submit_form(test_user.username, test_user.password)

    # User is redirected to welcome page and clicks continue.
    WelcomePage(browser).continue_link.click()

    # User is redirected to create page.
    create_page = CreatePage(browser)

    # User enters post with missing title and sees error.
    create_page.submit_form('', 'asdfasdfdsfasdfasdf')
    assert create_page.get_error_message() == 'Invalid title'

    # User enters post with missing post and sees error.
    create_page.submit_form('a title', '')
    assert create_page.get_error_message() == 'Invalid content'

    # User enters valid post and is redirected to post page where post is
    # visible, and date of post is visible.
    title = 'a title'
    content = (
        'asdf asdfas asdf asdfadfa\n'
        'asdfasdfasdf asdf asdf asf asdf\n'
        'asd f sdf sdfasfsdf asdf asdf as'
    )
    create_page.submit_form(title, content)
    post_date = datetime.utcnow().date()

    post_id = int(browser.current_url.split('/')[-1])
    blog_post_page = BlogPostPage(browser, post_id)
    assert blog_post_page.title == title
    assert blog_post_page.date == post_date
    assert blog_post_page.content == content.split('\n')
