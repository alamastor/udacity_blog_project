import base
from base import run_app, browser
from blog import auth
from pages import LoginPage, CreatePage


def create_post(run_app, browser):
    # User visits create post page.
    browser.get(base.MAIN_PAGE_URL + '/create')

    # User is not logged in and gets redirected to login page.
    login_page = LoginPage(browser) # This just creates page abstraction

    # User logs in.
    test_user = base.create_test_user
    login_page.submit_form(test_user.username, test_user.password)

    # User visit create post page again.
    browser.get(base.MAIN_PAGE_URL + '/create')

    # User enters post with missing title and sees error.
    assert 1 == 0

    # User enters post with missing post and sees error.

    # User enters valid post and is redirected to post page where post is
    # visible.

