import base
from base import run_app, browser
from login_page import LoginPage


def test_user_signup(run_app, browser):
    login_page = LoginPage(browser)

    # User visits signup page.
    login_page.go_to_login_page()

    # User tries to sign up without a username and sees an error.
    login_page.submit_form('', 'asdf', 'asdf', 'a@b.com')
    assert login_page.get_error_message() == 'Invalid username'

    # User tries to sign up without a password and sees an error.
    login_page.submit_form('person', '', '')
    assert login_page.get_error_message() == 'Invalid password'

    # User tries to sign up with missmatching password and sees an error.
    login_page.submit_form('person', 'asdf', 'asdd')
    assert login_page.get_error_message() == "Passwords don't match"

    # User tries to sign up with invalid eamil and sees an error.
    login_page.submit_form('person', 'asdf', 'asdf', 'asdfasdf')
    assert login_page.get_error_message() == 'Invalid email address'

    # User logs in valid credentials
    login_page.submit_form('person', 'asdf', 'asdf', 'a@b.com')

    # User is redirected and sees username in nav.
    browser.implicitly_wait(5)
    assert header_text == 'Bloggity!'
    assert 'person' in browser.find_element_by_class_tag('nav').text
