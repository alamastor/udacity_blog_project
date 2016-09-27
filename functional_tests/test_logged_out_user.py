from collections import namedtuple
from datetime import datetime

import pytest

import base
from base import run_app, browser
from pages import HomePage, BlogPostPage


@pytest.fixture
def add_posts():
    Field = namedtuple('Field', ['type', 'name', 'value'])
    base.create_test_blog_post('Post A', 'asdfasfklanwemfl;aknf')
    base.create_test_blog_post('Post X', 'asdfasfklamnmfgh')
    base.create_test_blog_post('Post N', 'asdfasfklanwemzxcvzcxv')

def test_user_can_view_posts(run_app, browser, add_posts):
    # User visits main page.
    home_page = HomePage(browser).visit_page()

    # User can see header and and mulitple posts.
    assert home_page.header.text == 'Bloggity!'

    assert home_page.blog_posts[0].title == 'Post N'
    assert home_page.blog_posts[2].title == 'Post A'

    assert len(home_page.blog_posts) == 3

    # User visits an individual blog post and can see content.
    home_page.blog_posts[0].click()

    post_id = int(browser.current_url.split('/')[-1])
    blog_post_page = BlogPostPage(browser, post_id)
    assert blog_post_page.title == 'Post N'
    assert blog_post_page.date == datetime.utcnow().date()
