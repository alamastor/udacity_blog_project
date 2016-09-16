import pytest
from selenium.webdriver.remote.errorhandler import NoSuchElementException

from pages import BlogPostPage, LoginPage, HomePage
import base
from base import run_app, browser


def test_blog_post(run_app, browser):
    # User logs in.
    test_user = base.create_test_user()
    login_page = LoginPage(browser)
    login_page.visit_page()
    test_user = base.create_test_user()
    login_page.submit_form(test_user.username, test_user.password)

    # Add posts to db.
    other_blog_post = base.create_test_blog_post('A Post', 'asdfasdl')
    blog_post = base.create_test_blog_post(
        'B Post', 'qwerqtqreqwr', test_user.user_id
    )

    # User visits a post by another user.
    blog_post_page = BlogPostPage(browser, other_blog_post)
    blog_post_page.visit_page()

    # Post is visible on page.
    assert blog_post_page.title == 'A Post'

    # Edit and delete buttons are not visible on post.
    with pytest.raises(NoSuchElementException) as e:
        blog_post_page.edit(content='nlkksdnf')
    assert 'post__edit' in e.value.msg

    with pytest.raises(NoSuchElementException) as e:
        blog_post_page.delete()
    assert 'post__delete' in e.value.msg

    # User visits a post by themself.
    blog_post_page = BlogPostPage(browser, blog_post)
    blog_post_page.visit_page()

    # Post is visible on page.
    assert blog_post_page.title == 'B Post'
    assert blog_post_page.content == 'qwerqtqreqwr'

    # User edits post.
    blog_post_page.edit(title='C Post', content='updated content')

    # Post is updated.
    assert blog_post_page.title == 'C Post'
    assert blog_post_page.content == 'updated content'

    # User deletes post.
    blog_post_page.delete()

    # User is redirected to home page, and post is gone.
    home_page = HomePage(browser)
    assert home_page.is_open()

    assert home_page.blog_posts[0].title == 'A Post'
    assert len(home_page.blog_posts) == 1
