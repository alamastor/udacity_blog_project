from collections import namedtuple
from datetime import datetime

import pytest
from lxml import html

from blog.views import HomePage
from blog.models import Post


@pytest.fixture
def testapp():
    import webapp2
    import webtest
    from google.appengine.ext import testbed
    from blog.main import ROUTER

    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    # TODO: Do I need a temp file here?
    testbed.init_datastore_v3_stub()
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


def test_main_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_main_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body


@pytest.fixture
def posts(mocker):
    Post = namedtuple('Post', ['title', 'content', 'datetime', 'url'])
    mocked_query = mocker.patch('blog.views.Post.query')
    mocked_query.return_value.fetch.return_value = [
        Post('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), '/posts/post-1'),
        Post('Post 2', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 11), '/posts/post-2'),
    ]


def test_main_page_shows_blog_posts(testapp, posts):
    body = testapp.get('/').normal_body
    assert 'Post 1' in body
    assert 'Post 2' in body
    assert body.count('post__content') == 2


def test_main_page_post_are_order_newest_to_oldest(testapp, posts):
    body = testapp.get('/').normal_body
    print(body)
    tree = html.fromstring(body)
    titles = tree.xpath('//h2[@class="post__title"]/a/text()')
    assert titles == ['Post 2', 'Post 1']


def test_main_has_links_to_individual_posts(testapp, posts):
    body = testapp.get('/').normal_body
    tree = html.fromstring(body)
    links = tree.xpath('//h2[@class="post__title"]/a/@href')
    assert links == ['/posts/post-2', '/posts/post-1']
