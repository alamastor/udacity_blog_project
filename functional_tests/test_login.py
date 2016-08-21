from collections import namedtuple

import pytest

import base
from base import run_app, browser


@pytest.fixture
def test_user():
    User = namedtuple('User', ['username', 'password'])
    test_user = User('Billy_Bob', '!Password')
    Field = namedtuple('Field', ['type', 'name', 'value'])
    base.write_to_db('User', (
        Field('string', 'username', test_user.username),
        Field('string', 'pw_hash', 'ea6b636e740f821220fe50263f127519a5185fe875df414bbe6b00de21a5b282'),
        Field('string', 'salt', '12345678'),
    ))
    return test_user


def test_user_login(run_app, browser, test_user):
    # User visits login page.
    browser.get(base.MAIN_PAGE_URL + '/login')

    # User logs trys to log in with invalid credentials.
    user_input = browser.find_element_by_name('username')
    pw_input = browser.find_element_by_name('password')
    submit = browser.find_element_by_xpath('//input[@type="submit"]')
    user_input.send_keys('fake')
    pw_input.send_keys('fake')
    submit.click()


    # Error message is displayed.
    error_text = browser.find_element_by_class_name('error').text
    assert error_text == 'Invalid login credentials.'

    # User logs in.
    user_input = browser.find_element_by_name('username')
    pw_input = browser.find_element_by_name('password')
    submit = browser.find_element_by_xpath('//input[@type="submit"]')
    user_input.send_keys(test_user.username)
    pw_input.send_keys(test_user.password)
    submit.click()

    # User is redirected to home page
    browser.implicitly_wait(5)
    header_text = browser.find_element_by_tag_name('h1').text
    assert header_text == 'Bloggity!'

    # User is show as logged in.
    assert 0
