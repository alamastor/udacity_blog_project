import pytest
from selenium.webdriver.remote.errorhandler import NoSuchElementException

from pages import BlogPostPage, LoginPage, HomePage, WelcomePage
import base
from base import run_app, browser


def test_like_posts(run_app, browser):
    test_user = base.create_test_user()

    # Add posts to db.
    other_blog_post = base.create_test_blog_post('A Post', 'asdfasdl')
    blog_post = base.create_test_blog_post(
        'B Post', 'qwerqtqreqwr', test_user.user_id
    )

    # User visits one of their posts.
    blog_post_page = BlogPostPage(browser, blog_post)
    blog_post_page.visit_page()

    # User clicks like, but is not logged in so is redirected to login.
    blog_post_page.like_button.click()

    login_page = LoginPage(browser)
    assert login_page.is_open()

    # User logs in.
    login_page.submit_form(test_user.username, test_user.password)

    # User is redirected to welcome page and clicks continue.
    WelcomePage(browser).continue_link.click()

    # User is redirected to blog post page.
    assert blog_post_page.is_open()

    # Like button is no longer visible, as user can't like own post.
    with pytest.raises(NoSuchElementException) as e:
        blog_post_page.like_button
    assert 'post__like' in e.value.msg

    # User clicks like to home page, and goes to other post.
    blog_post_page.home_link.click()
    home_page = HomePage(browser)
    post_id = home_page.blog_posts[1].post_id
    home_page.blog_posts[1].click()
    blog_post_page = BlogPostPage(browser, post_id)
    assert blog_post_page.is_open()

    # User clicks like.
    blog_post_page.like_button.click()

    # The post now has one like
    assert blog_post_page.likes == 1

    # The like button is replaced with an unlike button. User presses unlike,
    # and is like button is now visible.
    blog_post_page.unlike_button.click()
    assert blog_post_page.like_button
