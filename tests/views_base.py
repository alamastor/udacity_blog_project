from collections import namedtuple
from datetime import datetime

import pytest
import webtest
import webapp2

from main import ROUTER
from models.user import User
from utils import auth


@pytest.fixture
def testapp():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    testbed.init_datastore_v3_stub()
    testbed.init_memcache_stub()
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


@pytest.fixture
def fake_user():
    user = User(
        username='Billy_Bob',
        pw_hash='ea6b636e740f821220fe50263f127519a5185fe875df414bbe6b00de21a5b281',
        salt='12345678'
    )
    user.put()
    return user


@pytest.fixture
def mock_BlogPost(mocker, user_id=2):
    # Patch this for differect tests that use it.
    mocked_BlogPost_post_page = mocker.patch('views.blog_post_page.BlogPost', autospec=True)
    mocked_BlogPost_create_edit_page = mocker.patch('views.create_edit_page.BlogPost', autospec=True)
    mocked_BlogPost_comment_page = mocker.patch('views.comment_page.BlogPost', autospec=True)
    mock_post = mocker.Mock()
    key = mocker.Mock(return_value='A1')
    key.id = mocker.Mock(return_value=1)
    type(mock_post).title = 'Post 1'
    type(mock_post).content = 'dfjals;dfjawpoefinasdni'
    type(mock_post).paragraphs = ['dfjals;dfjawpoefinasdni']
    type(mock_post).datetime = datetime(2016, 8, 10)
    type(mock_post).key = key
    type(mock_post).user_id = user_id

    mocked_BlogPost_post_page.get_by_id.return_value = mock_post
    mocked_BlogPost_create_edit_page.get_by_id.return_value = mock_post
    mocked_BlogPost_comment_page.get_by_id.return_value = mock_post
    return mock_post


def logged_in_get(testapp, url, user_id):
    testapp.set_cookie('sess', '%s|%s' % (user_id, auth.make_secure_val(user_id)))
    return testapp.get(url)


def logged_in_get_post_page(testapp, post_id, user_id):
    return logged_in_get(testapp, '/post/%i' % post_id, user_id)


def logged_in_post(testapp, url, user_id, post_dict={}):
    return testapp.post(
        url,
        post_dict,
        headers={
            'Cookie': 'sess=%s|%s; Path=/' % (
                user_id, auth.make_secure_val(user_id)
            )
        },
    )


@pytest.fixture
def mock_comments(mocker):
    Comment = namedtuple('Comment', [
        'comment', 'paragraphs', 'datetime', 'formatted_date', 'username'
    ])
    mocked_Comment = mocker.patch('views.blog_post_page.Comment', autospec=True)
    mocked_Comment.get_by_post_key.return_value = [
        Comment('A comment', ['A comment'], datetime(2014, 1, 1), '1-Jan-2014', 'A user'),
        Comment('B comment', ['B comment'], datetime(2015, 1, 1), '1-Jan-2015', 'B user'),
        Comment('C comment', ['C comment'], datetime(2014, 1, 2), '2-Jan-2014', 'C user'),
    ]


@pytest.fixture
def mock_Like(mocker):
    mocked_Like = mocker.patch('views.blog_post_page.Like', autospec=True)
    mock_like = mocker.Mock()
    type(mock_like).put = mocker.Mock()
    mocked_Like.return_value = mock_like
    return mocked_Like


def cookie_set(response, cookie_name, cookie_val):
    for cookie in response.headers.getall('Set-Cookie'):
        name = cookie.split(';')[0].split('=')[0]
        val = cookie.split(';')[0].split('=')[1]
        if name == cookie_name:
            return val == cookie_val
    return False  # correct cookie not found
