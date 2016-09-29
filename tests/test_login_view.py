from collections import namedtuple

import pytest

from blog.models import BlogPost, User
from blog import auth
import views_base
from views_base import testapp, fake_user


@pytest.fixture
def mock_valid_User(mocker, mock):
    User = namedtuple('User', ['username', 'password'])
    mock_user = User('Billy_Bob', '!Password')
    DbUser = namedtuple('DbUser', ['username', 'pw_hash', 'salt', 'key'])
    mocked_get_by_username = mocker.patch('blog.views.views.User.get_by_username')
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
    mocked_get_by_username = mocker.patch('blog.views.views.User.get_by_username')
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
    mocked_query_by_username = mocker.patch('blog.views.views.User.get_by_username')
    mocked_query_by_username.return_value = None
    return mock_user


@pytest.fixture
def mock_login(mocker):
    return mocker.patch('blog.views.views.AuthHandler.log_user_in')


def test_login_page_returns_200(testapp):
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


def post_user_to_login(testapp, user, cookie_dict={}):
    cookies = ''
    for key, val in cookie_dict.iteritems():
        cookies += '%s=%s;' % (key, val)
    return testapp.post(
        '/login',
        dict(username=user.username, password=user.password),
        headers={'Cookie': cookies}
    )


def test_login_with_correct_credentials_redirects_to_welcome(testapp, mock_valid_User):
    res = post_user_to_login(testapp, mock_valid_User)
    assert res.status_int == 302
    assert res.location.split('/')[-1] == 'welcome'


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
    assert fake_user.username in response.html.nav.text


def test_get_with_referer_sets_after_login_cookie(testapp):
    res = testapp.get('/login', extra_environ={'HTTP_REFERER': '/asdf'})
    assert views_base.cookie_set(res, 'after_login', '/asdf')


def test_get_with_after_login_cookie_set_does_not_overwrite(testapp):
    testapp.set_cookie('after_login', '/zxcv')
    res = testapp.get(
        '/login',
        extra_environ={'HTTP_REFERER': '/asdf'}
    )
    assert testapp.cookies['after_login'] == '"/zxcv"'
    assert not views_base.cookie_set(res, 'after_login', '/zxcv')
