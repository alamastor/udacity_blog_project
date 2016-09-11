import pytest
from bs4 import BeautifulSoup
from webtest import AppError

from views_base import testapp, fake_user
from blog import auth


@pytest.fixture
def get_create_logged_in(testapp, fake_user):
    user_id = fake_user.key.id()
    return testapp.get('/create', headers={
        'Cookie': 'sess=%s|%s; Path=/' % (
            user_id, auth.make_secure_val(user_id)
        )
    })


def post_logged_in(testapp, fake_user, post_data={}):
    user_id = fake_user.key.id()
    return testapp.post('/create', post_data, headers={
        'Cookie': 'sess=%s|%s; Path=/' % (
            user_id, auth.make_secure_val(user_id)
        )
    })


def test_create_view_redirects_to_signup_if_not_logged_in(testapp):
    response = testapp.get('/create')
    assert response.status_int == 302
    assert response.location.split('/')[-1] == 'login'


def test_create_view_returns_200_if_logged_in(get_create_logged_in):
    assert get_create_logged_in.status_int == 200


def test_create_view_has_correct_form_fields(get_create_logged_in):
    soup = BeautifulSoup(get_create_logged_in.normal_body, 'html.parser')
    forms = soup.find_all('form')
    assert len(forms) == 1

    form = forms[0]
    assert form.find('input', {'name': 'title'}) is not None
    assert form.find('textarea', {'name': 'content'}) is not None


def test_post_by_logged_out_user_raises_401(testapp):
    with pytest.raises(AppError) as excinfo:
        testapp.post('/create')
    assert '401' in str(excinfo.value)


def test_post_with_invalid_title_shows_error(testapp, fake_user):
    response = post_logged_in(testapp, fake_user, {
        'title': 'zx', 'content': 'asdfasdf afdsasdfasdf asdfadsf'
    })
    assert 'Invalid title' in response.normal_body


def test_post_with_invalid_content_shows_error(testapp, fake_user):
    response = post_logged_in(testapp, fake_user, {
        'title': 'zxasdfas', 'content': 'asd'
    })
    assert 'Invalid content' in response.normal_body


def test_invalid_post_keeps_content_in_form(testapp, fake_user):
    response = post_logged_in(testapp, fake_user, {
        'title': 'axa', 'content': 'qwe'
    })
    assert 'axa' in response.normal_body
    assert 'qwe' in response.normal_body


def test_valid_post_calls_BlogPost(testapp, fake_user, mocker):
    mock_BlogPost = mocker.patch('blog.views.BlogPost', autospec=True)
    mock_BlogPost.return_value.key.id = mocker.Mock(return_value=1)
    post_logged_in(testapp, fake_user, {
        'title': 'axasdf', 'content': 'qwerqwer'
    })
    mock_BlogPost.assert_called_once()
    mock_BlogPost.return_value.put.assert_called_once()


def test_valid_post_redirects_to_post_page(testapp, fake_user, mocker):
    mock_BlogPost = mocker.patch('blog.views.BlogPost', autospec=True)
    mock_BlogPost.return_value.key.id = mocker.Mock(return_value=1)
    response = post_logged_in(testapp, fake_user, {
        'title': 'axasdf', 'content': 'qwerqwer'
    })
    assert response.status_int == 302
    assert response.location.split('/')[-2:] == ['post', '1']
