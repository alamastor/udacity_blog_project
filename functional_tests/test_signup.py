import base
from base import run_app, browser
from pages import SignUpPage


def test_user_signup(run_app, browser):
    signup_page = SignUpPage(browser)

    # User visits signup page.
    signup_page.visit_page()

    # User tries to sign up without a username and sees an error.
    signup_page.submit_form('', 'asdf', 'asdf', 'a@b.com')
    assert signup_page.get_error_message() == 'Invalid username'

    # User tries to sign up without a password and sees an error.
    signup_page.submit_form('person', '', '')
    assert signup_page.get_error_message() == 'Invalid password'

    # User tries to sign up with missmatching password and sees an error.
    signup_page.submit_form('person', 'asdf', 'asdd')
    assert signup_page.get_error_message() == "Passwords didn't match"

    # User tries to sign up with invalid eamil and sees an error.
    signup_page.submit_form('person', 'asdfxx', 'asdfxx', 'asdfasdf')
    assert signup_page.get_error_message() == 'Invalid email address'

    # User logs in valid credentials
    signup_page.submit_form('person', 'asdf', 'asdf', 'a@b.com')

    # User is redirected and sees username in nav.
    browser.implicitly_wait(5)
    header_text = browser.find_element_by_tag_name('h1').text
    assert header_text == 'Bloggity!'
    assert 'person' in browser.find_element_by_tag_name('nav').text
