from collections import namedtuple

import pytest
import requests
from lxml import html

MAIN_PAGE_URL = 'localhost:8080'
DATASTORE_URL = 'http://localhost:8000/datastore'

@pytest.fixture
def browser():
    from selenium import webdriver
    browser = webdriver.Firefox()
    yield browser

    browser.quit()


@pytest.fixture
def run_app():
    import subprocess
    app_proc = subprocess.Popen([
        'dev_appserver.py',
        '--clear_datastore=yes',
        '--datastore_path=/tmp/temp_blog_datastore',
        'blog'
    ])
    yield

    app_proc.terminate()


def write_to_db(entity_kind, fields):
    page = requests.get('%s?edit=%s' % (DATASTORE_URL, entity_kind))
    tree = html.fromstring(page.content)
    xsrf_token = tree.xpath('//input[@name="xsrf_token"]')[0].value
    post_data = {
        'kind': entity_kind,
        'xsrf_token': xsrf_token
    }
    for field in fields:
        post_data['%s|%s' % (field.type, field.name)] = field.value
    r = requests.post(DATASTORE_URL + '/edit', data=post_data)
    print(r)


@pytest.fixture
def add_posts():
    Field = namedtuple('Field', ['type', 'name', 'value'])
    write_to_db('Post', [
        Field('string', 'title', 'Post 1'),
        Field('Text', 'content', 'asdfasfklanwemfl;aknf'),
        Field('datetime', 'datetime', '2016-8-10 06:12:23')
    ])
    write_to_db('Post', [
        Field('string', 'title', 'Post 2'),
        Field('Text', 'content', 'asdfasfklanwemfl;aknf'),
        Field('datetime', 'datetime', '2016-8-11 06:12:23')
    ])


def test_user_can_view_posts(run_app, browser, add_posts):
    # User visits main page.
    browser.get(MAIN_PAGE_URL)

    # User can see header and and mulitple posts.
    header_text = browser.find_element_by_tag_name('h1').text
    assert header_text == 'Bloggity!'

    post_titles = browser.find_elements_by_class_name('post__title')
    assert post_titles[0].text == 'Post 2'
    assert post_titles[1].text == 'Post 1'

    post_content = browser.find_elements_by_class_name('post__content')
    assert len(post_content) == 2

    # User visits an individual blog post and can see content.
    assert 0

    # User write comment on blog post.

    # Comment is now visible on page.
