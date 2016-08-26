from collections import namedtuple
from datetime import datetime

import pytest
import webtest
import webapp2
from bs4 import BeautifulSoup
2
from blog.main import ROUTER
from blog.views import HomePage
from blog.models import Post, User
from blog import auth


@pytest.fixture
def testapp():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    testbed.init_datastore_v3_stub()
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


def test_home_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_home_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body


@pytest.fixture
def mock_Post_fetch(mocker):
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
def mock_Post_get_by_id(mocker):
    Post = namedtuple('Post', ['title', 'content', 'datetime', 'key'])
    mocked_get = mocker.patch('blog.views.Post.get_by_id')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    mocked_get.return_value = Post('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1)


@pytest.fixture
def mock_valid_User(mocker, mock):
    User = namedtuple('User', ['username', 'password'])
    mock_user = User('Billy_Bob', '!Password')
    DbUser = namedtuple('DbUser', ['username', 'pw_hash', 'salt', 'key'])
    mocked_get_by_username = mocker.patch('blog.views.User.get_by_username')
    mock_key = mock
    mock_key.id = mocker.Mock(return_value=1)
    mocked_get_by_username.return_value = DbUser(
        mock_user.username,
        'ea6b636e740f821220fe50263f127519a5185fe875df414bbe6b00de21a5b282',
        '12345678',
        mock_key
    )
    return mock_user


@pytest.fixture
def mock_invalid_User(mocker):
    User = namedtuple('User', ['username', 'password'])
    mock_user = User('Billy_Bob', '!Password')
    DbUser = namedtuple('DbUser', ['username', 'pw_hash', 'salt'])
    mocked_get_by_username = mocker.patch('blog.views.User.get_by_username')
    mocked_get_by_username.return_value = DbUser(
        mock_user.username,
        'ea6b636e740f821220fe50263f127519a5185fe875df414bbe6b00de21a5b281',
        '12345678'
    )
    return mock_user


@pytest.fixture
def mock_non_existant_User(mocker):
    User = namedtuple('User', ['username', 'password'])
    mock_user = User('Billy_Bob', '!passwrd')
    mocked_query_by_username = mocker.patch('blog.views.User.get_by_username')
    mocked_query_by_username.return_value = None
    return mock_user


@pytest.fixture
def mock_login(mocker):
    return mocker.patch('blog.views.AuthHandler.log_user_in')


@pytest.fixture
def fake_user():
    user = User(
        username='Billy_Bob',
        pw_hash='ea6b636e740f821220fe50263f127519a5185fe875df414bbe6b00de21a5b281',
        salt='12345678'
    )
    user.put()
    return user


def test_home_page_shows_blog_posts(testapp, mock_Post_fetch):
    body = testapp.get('/').normal_body
    assert 'Post 1' in body
    assert 'Post 2' in body
    assert body.count('post__content') == 2


def test_home_page_post_are_order_newest_to_oldest(testapp, mock_Post_fetch):
    body = testapp.get('/').normal_body
    soup = BeautifulSoup(body, 'html.parser')
    titles = [x.text for x in soup.find_all('h2', {'class': 'post__title'})]
    assert titles == ['Post 2', 'Post 1']


def test_home_has_links_to_individual_posts(testapp, mock_Post_fetch):
    body = testapp.get('/').normal_body
    soup = BeautifulSoup(body, 'html.parser')
    links = [x.a['href'] for x in soup.find_all('h2', {'class': 'post__title'})]
    assert links == ['/post/2', '/post/1']


def test_get_post_returns_404_if_post_does_not_exist(testapp):
    with pytest.raises(webtest.AppError) as e:
        testapp.get('/posts/asdfadsfadsf')
        assert '404' in e.value


def test_get_post_returns_200_if_post_exists(testapp, mock_Post_get_by_id):
    assert testapp.get('/post/1').status_int == 200


def test_login_returns_200(testapp):
    assert testapp.get('/login').status_int == 200


def test_login_has_form(testapp):
    body = testapp.get('/login').normal_body
    assert '<form' in body


def test_login_returns_200_on_invalid_post(testapp):
    assert testapp.post('/login').status_int == 200


def test_login_shows_error_on_missing_username_post(testapp):
    body = testapp.post('/login', dict(password='asdfds')).normal_body
    assert 'Invalid' in body


def test_login_shows_error_on_missing_password_post(testapp):
    body = testapp.post('/login', dict(username='fsdafa')).normal_body
    assert 'Invalid' in body


def post_user_to_login(testapp, user):
    return testapp.post('/login', dict(
        username=user.username, password=user.password
    ))


def test_login_with_correct_credentials_redirects(testapp, mock_valid_User):
    assert post_user_to_login(testapp, mock_valid_User).status_int == 302


def test_login_shows_error_on_non_existant_user(testapp, mock_non_existant_User):
    response = post_user_to_login(testapp, mock_non_existant_User)
    assert 'Invalid' in response.normal_body


def test_login_shows_error_on_invalid_user(testapp, mock_invalid_User):
    response = post_user_to_login(testapp, mock_invalid_User)
    assert 'Invalid' in response.normal_body


def test_valid_User_response_contains_cookie(testapp, mock_valid_User):
    assert 'Set-Cookie' in post_user_to_login(testapp, mock_valid_User).headers


def test_login_cookie_has_name_sess(testapp, mock_valid_User):
    cookie = post_user_to_login(testapp, mock_valid_User).headers['Set-Cookie']
    assert cookie.split('=')[0] == 'sess'


def test_login_with_valid_user_calls_login_meth(testapp, mock_valid_User, mock_login):
    post_user_to_login(testapp, mock_valid_User)
    mock_login.assert_called_once()


def test_logged_in_user_has_username_displayed_in_nav(testapp, fake_user):
    user_id = fake_user.key.id()
    response = testapp.get('/', headers={
        'Cookie': 'sess=%s|%s; Path=/' % (user_id, auth.make_secure_val(user_id))
    })
    soup = BeautifulSoup(response.body, 'html.parser')
    assert fake_user.username in soup.nav.text
