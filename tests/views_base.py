from collections import namedtuple
from datetime import datetime

import pytest
import webtest
import webapp2

from blog.main import ROUTER
from blog.models import User
from blog import auth


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
    mocked_BlogPost = mocker.patch('blog.views.BlogPost', autospec=True)
    mock_post = mocker.Mock()
    key = mocker.Mock(return_value='A1')
    key.id = mocker.Mock(return_value=1)
    type(mock_post).title = 'Post 1'
    type(mock_post).content = 'dfjals;dfjawpoefinasdni'
    type(mock_post).datetime = datetime(2016, 8, 10)
    type(mock_post).key = key
    type(mock_post).user_id = user_id

    mocked_BlogPost.get_by_id.return_value = mock_post
    return mock_post


def logged_in_get(testapp, url, user_id):
    return testapp.get(url, headers={
        'Cookie': 'sess=%s|%s; Path=/' % (
            user_id, auth.make_secure_val(user_id)
        )
    })


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
        'comment', 'datetime', 'formatted_date', 'username'
    ])
    mocked_Comment = mocker.patch('blog.views.Comment', autospec=True)
    mocked_Comment.get_by_post_key.return_value = [
        Comment('A comment', datetime(2014, 1, 1), '1-Jan-2014', 'A user'),
        Comment('B comment', datetime(2015, 1, 1), '1-Jan-2015', 'B user'),
        Comment('C comment', datetime(2014, 1, 2), '2-Jan-2014', 'C user'),
    ]
