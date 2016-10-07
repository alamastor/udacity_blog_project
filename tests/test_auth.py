import pytest

from blog.utils import auth
from blog.models.user import User


@pytest.fixture
def testdb():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    testbed.init_datastore_v3_stub()
    testbed.init_memcache_stub()


def test_make_pw_hash_returns_256_bit_str():
    digest = auth.make_pw_hash('user', 'pass', '1231')
    assert type(digest) is str
    assert len(digest) == 64


def test_make_secure_val_returns_256_bit_str():
    digest = auth.make_secure_val(123)
    assert type(digest) is str
    assert len(digest) == 64


def test_check_secure_val_returns_true_for_valid_input():
    digest = auth.make_secure_val(123)
    assert auth.check_secure_val(123, digest) is True


def test_check_secure_val_returns_false_for_invalid_input():
    digest = auth.make_secure_val(123)
    assert auth.check_secure_val(125, digest) is False


@pytest.fixture
def mock_User(mocker):
    mock_User = mocker.patch('blog.utils.auth.User', autospec=True)
    mock_User.return_value.key.id = mocker.Mock(return_value=100)
    mock_User.get_by_username.return_value = []

    return mock_User


def test_create_user_calls_User_and_put(mock_User):
    auth.create_user('user', 'password')

    mock_User.assert_called_once()
    mock_User.return_value.put.assert_called_once()


def test_create_user_does_not_call_User_with_raw_pass(mock_User):
    auth.create_user('user', 'pass')
    assert mock_User.call_args[1]['pw_hash'] != 'pass'


def test_create_user_calls_make_salt(mocker, mock_User):
    mock_make_salt = mocker.patch('blog.utils.auth.make_salt')
    mock_make_salt.return_value = '1'

    auth.create_user('user', 'pass')

    mock_make_salt.assert_called_once()


def test_make_salt_calls_os_urandom(mocker):
    mock_urandom = mocker.patch('os.urandom')
    mock_urandom.return_value = '123'

    auth.make_salt()
    mock_urandom.assert_called_once()


def test_create_user_calls_make_pw_hash_with_correct_args(mocker, mock_User):
    mock_pw_hash = mocker.patch('blog.utils.auth.make_pw_hash')
    mock_salt = mocker.patch('blog.utils.auth.make_salt').return_value

    auth.create_user('user', 'pass')

    mock_pw_hash.assert_called_once_with('user', 'pass', mock_salt)


def test_create_user_calls_User_with_email_if_arg(mocker, mock):
    mock_User = mocker.patch('blog.utils.auth.User')
    mock_User.get_by_username.return_value = []

    auth.create_user('user', 'pass', 'a@b.com')

    mock_User.assert_called_once_with(
        username='user', pw_hash=mock.ANY, salt=mock.ANY, email='a@b.com'
    )


def test_create_user_return_user_id(mocker, mock_User):
    assert auth.create_user('user', 'pass') == mock_User().key.id()


def test_duplicate_user_raises(testdb):
    User(username='asdf', pw_hash='asdf', salt='asdf').put()
    with pytest.raises(auth.UserAlreadyExists):
        auth.create_user('asdf', 'qwerqwer')
