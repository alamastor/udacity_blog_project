from collections import namedtuple
from datetime import datetime

import pytest
from lxml import html
import webtest
import webapp2
2
from blog.main import ROUTER
from blog.views import HomePage
from blog.models import Post


@pytest.fixture
def testapp():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    # TODO: Do I need a temp file here?
    testbed.init_datastore_v3_stub()
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


def test_home_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_home_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body


@pytest.fixture
def mock_posts_fetch(mocker):
    Post = namedtuple('Post', ['title', 'content', 'datetime', 'key'])
    mocked_query = mocker.patch('blog.views.Post.query')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    keyId2 = mocker.Mock()
    keyId2.id = mocker.Mock(return_value=2)
    mocked_query.return_value.fetch.return_value = [
        Post('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1),
        Post('Post 2', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 11), keyId2),
    ]


@pytest.fixture
def mock_posts_get_by_id(mocker):
    Post = namedtuple('Post', ['title', 'content', 'datetime', 'key'])
    mocked_get = mocker.patch('blog.views.Post.get_by_id')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    mocked_get.return_value = Post('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1)


def test_home_page_shows_blog_posts(testapp, mock_posts_fetch):
    body = testapp.get('/').normal_body
    assert 'Post 1' in body
    assert 'Post 2' in body
    assert body.count('post__content') == 2


def test_home_page_post_are_order_newest_to_oldest(testapp, mock_posts_fetch):
    body = testapp.get('/').normal_body
    print(body)
    tree = html.fromstring(body)
    titles = tree.xpath('//h2[@class="post__title"]/a/text()')
    assert titles == ['Post 2', 'Post 1']


def test_home_has_links_to_individual_posts(testapp, mock_posts_fetch):
    body = testapp.get('/').normal_body
    tree = html.fromstring(body)
    links = tree.xpath('//h2[@class="post__title"]/a/@href')
    assert links == ['/posts/2', '/posts/1']


def test_get_post_returns_404_if_post_does_not_exist(testapp):
    with pytest.raises(webtest.AppError) as e:
        testapp.get('/posts/asdfadsfadsf')
        assert '404' in e.value


def test_get_post_returns_200_if_post_exists(testapp, mock_posts_get_by_id):
    assert testapp.get('/post/1').status_int == 200
