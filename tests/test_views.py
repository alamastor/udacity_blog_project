from collections import namedtuple

import pytest

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
    # TODO: Do I need a temp file here
    testbed.init_datastore_v3_stub()
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


def test_main_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_main_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body


def test_main_page_shows_blog_posts(testapp, mocker):
    Post = namedtuple('Post', ['title', 'content'])
    mocked_query = mocker.patch('blog.views.Post.query')
    mocked_query.return_value.fetch.return_value = [
        Post('Post 1', 'dfjals;dfjawpoefinasdni'),
        Post('Post 2', 'dfjals;dfjawpoefinasdni'),
    ]

    body = testapp.get('/').normal_body
    assert 'Post 1' in body
    assert 'Post 2' in body
    assert body.count('post__content') == 2
