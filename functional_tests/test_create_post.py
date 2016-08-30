from datetime import date, datetime

import base
from base import run_app, browser
from blog import auth
from pages import LoginPage, CreatePage


def test_create_post(run_app, browser):
    create_page = CreatePage(browser)
    # User visits create post page.
    create_page.visit_page()

    # User is not logged in and gets redirected to login page.
    login_page = LoginPage(browser)

    # User logs in.
    test_user = base.create_test_user()
    login_page.submit_form(test_user.username, test_user.password)

    # User visit create post page again.
    create_page.visit_page()

    # User enters post with missing title and sees error.
    create_page.submit_form('', 'asdfasdfdsfasdfasdf')
    assert create_page.get_error_message() == 'Invalid title'

    # User enters post with missing post and sees error.
    create_page.submit_form('a title', '')
    assert create_page.get_error_message() == 'Invalid content'

    # User enters valid post and is redirected to post page where post is
    # visible, and date of post is visible.
    title = 'a title'
    content = (
        'asdf asdfas asdf asdfadfa\n'
        'asdfasdfasdf asdf asdf asf asdf\n'
        'asd f sdf sdfasfsdf asdf asdf as'
    )
    create_page.submit_form(title, content)
    post_date = date.today()
    post_date_on_page = datetime.strptime(
        browser.find_element_by_class_name('post__date').text,
        '%d-%b-%Y'
    ).date()
    assert post_date == post_date_on_page
    assert browser.find_element_by_class_name('post__title').text == title
    assert datetime.strptime(
        browser.find_element_by_class_name('post__date').text, '%d-%b-%Y'
    ).date() == post_date
    post_content = browser.find_element_by_class_name('post__content').text
    assert  post_content.encode('ascii') == content.replace('\n', ' <br>')
