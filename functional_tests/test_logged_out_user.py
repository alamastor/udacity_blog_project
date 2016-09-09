from collections import namedtuple
from datetime import datetime

import pytest

import base
from base import run_app, browser


@pytest.fixture
def add_posts():
    Field = namedtuple('Field', ['type', 'name', 'value'])
    base.create_test_blog_post('Post 1', 'asdfasfklanwemfl;aknf')
    base.create_test_blog_post('Post 2', 'asdfasfklanwemfl;aknf')

def test_user_can_view_posts(run_app, browser, add_posts):
    # User visits main page.
    browser.get(base.MAIN_PAGE_URL)

    # User can see header and and mulitple posts.
    header_text = browser.find_element_by_tag_name('h1').text
    assert header_text == 'Bloggity!'

    post_titles = browser.find_elements_by_class_name('post__title')
    assert post_titles[0].text == 'Post 2'
    assert post_titles[1].text == 'Post 1'

    post_content = browser.find_elements_by_class_name('post__content')
    assert len(post_content) == 2

    # User visits an individual blog post and can see content.
    post_titles[0].find_element_by_tag_name('a').click()
    header_text = browser.find_element_by_tag_name('h1').text
    post_time = browser.find_element_by_class_name('post__date').text
    assert header_text == 'Post 2'
    assert post_time == datetime.now().strftime('%-d-%b-%Y')
