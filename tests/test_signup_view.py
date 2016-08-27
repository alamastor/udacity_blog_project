import pytest
from bs4 import BeautifulSoup
import jinja2

from views_base import testapp


def test_signup_page_returns_200(testapp):
    assert testapp.get('/signup').status_int == 200


def test_signup_page_has_form_with_correct_fields(testapp):
    body = testapp.get('/signup').normal_body
    soup = BeautifulSoup(body, 'html.parser')
    forms = soup.find_all('form')
    assert len(forms) == 1

    form = forms[0]
    assert form.find('input', {'name': 'username'}) is not None
    assert form.find('input', {'name': 'password'}) is not None
    assert form.find('input', {'name': 'verify'}) is not None
    assert form.find('input', {'name': 'email'}) is not None


def post_to_signup(testapp, **kwargs):
    return testapp.post('/signup', kwargs)

def test_signup_returns_200_on_invalid_post(testapp):
    assert post_to_signup(testapp).status_int == 200


def test_post_with_invalid_username_displays_error(testapp):
    assert 'Invalid username' in post_to_signup(
        testapp, username='x'
    ).normal_body


def test_post_with_missing_password_displays_error(testapp):
    assert 'Invalid password' in post_to_signup(
        testapp,
        username='sadfas',
        password='ax',
    ).normal_body


def test_post_with_missmatching_passwords_displays_error(testapp):
    assert jinja2.escape("Passwords didn't match") in post_to_signup(
        testapp,
        username='sadfas',
        password='axaxax',
        verify='asdfasdfas'
    ).normal_body


def test_post_with_invalid_email_displays_error(testapp):
    assert 'Invalid email' in post_to_signup(
        testapp,
        username='sadfas',
        password='axaxax',
        verify='axaxax',
        email='asdfasd'
    ).normal_body


def test_invalid_post_keeps_username_and_email_in_form(testapp):
    body =  post_to_signup(
        testapp,
        username='sadfas',
        password='axaxax',
        email='asdfasd'
    ).normal_body

    soup = BeautifulSoup(body, 'html.parser')
    form = soup.form
    assert form.find('input', {'name': 'username'})['value'] == 'sadfas'
    assert form.find('input', {'name': 'email'})['value'] == 'asdfasd'


def valid_post(testapp):
    return post_to_signup(
        testapp,
        username='sadfas',
        password='axaxax',
        verify='axaxax',
        email='asdf@x.com'
    )


def test_valid_post_redirects(testapp):
    assert valid_post(testapp).status_int == 302


def test_valid_post_calls_create_user(testapp, mocker):
    mock_create_user = mocker.patch('blog.auth.create_user')
    valid_post(testapp)
    mock_create_user.assert_called_once()


def test_valid_post_calls_login(testapp, mocker):
    mock_login = mocker.patch('blog.views.AuthHandler.log_user_in')
    valid_post(testapp)
    mock_login.assert_called_once()
