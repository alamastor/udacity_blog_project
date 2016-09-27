import pytest

import base
from base import run_app, browser
from pages import LoginPage, HomePage, WelcomePage


@pytest.fixture
def test_user():
    return base.create_test_user()


def test_user_login(run_app, browser, test_user):
    # User visits login page.
    login_page = LoginPage(browser)
    login_page.visit_page()

    # User trys to log in with invalid credentials.
    login_page.submit_form('fake', 'fake')
    # Error message is displayed.
    assert login_page.get_error_message() == 'Invalid login credentials.'

    # User logs in.
    login_page.submit_form(test_user.username, test_user.password)

    # User is redirected to welcome page
    welcome_page = WelcomePage(browser)
    assert welcome_page.is_open()
    assert browser.find_element_by_class_name('welcome-header').text == 'Welcome %s!' % test_user.username

    # User clicks continue and sees username in nav.
    welcome_page.continue_link.click()
    home_page = HomePage(browser)
    assert home_page.header.text == 'Bloggity!'

    # User is shown as logged in.
    assert test_user.username in browser.find_element_by_tag_name('nav').text

    # User logs out.
    home_page.logout_button.click()

    # User is logged out.
    assert home_page.login_button
