from datetime import datetime

import pytest
from selenium.webdriver.remote.errorhandler import NoSuchElementException

from pages import BlogPostPage, LoginPage
import base
from base import run_app, browser


def test_commenting_page(run_app, browser):
    # Add some posts to db.
    base.create_test_blog_post('Post 1', 'asdfasdfa')
    other_post_id = base.create_test_blog_post('Post 2', 'asdfasdfadf')
    post_id = base.create_test_blog_post('Post 3', 'asdfasfklanwemf')

    # Add comments to those posts.
    base.create_test_comment(other_post_id, 'weqrqewr')
    base.create_test_comment(post_id, 'COMMENT CONTENT')
    base.create_test_comment(post_id, 'asdfasdf')
    base.create_test_comment(post_id, 'wexxrqewr')

    # User visit post page.
    post_page = BlogPostPage(browser, post_id)
    post_page.visit_page()

    # Post is visible on page.
    assert post_page.title == 'Post 3'

    # Three comments are visible on the page.
    comments = post_page.comments
    assert len(comments) == 3

    # The first comment has the correct content.
    assert comments[0].comment == 'COMMENT CONTENT'

    # The user is not logged in so warning is visible.
    login_message = browser.find_element_by_class_name('login-message').text
    assert login_message == 'You must be logged in to comment.'
    # No comment box is visible.
    with pytest.raises(NoSuchElementException):
        browser.find_element_by_class_name('add-comment')

    # User logs in.
    post_page.login_button.click()
    login_page = LoginPage(browser)
    test_user = base.create_test_user()
    login_page.submit_form(test_user.username, test_user.password)

    # User is redirected to post and writes a comment.
    post_page.write_comment('A mediocre comment')

    # The comment is now visible on the page.
    comments = post_page.comments
    assert len(comments) == 4
    assert comments[3].comment == 'A mediocre comment'

    # The user decides to edit the comment.
    # Only comments by that user have edit buttons
    with pytest.raises(NoSuchElementException):
        comments[0].edit('')
    # The comment can be edited.
    comments[3].edit('A slightly better comment')

    # The updated comment is now visible on the page.
    comments = post_page.comments
    assert len(comments) == 4
    assert comments[3].comment == 'A slightly better comment'

    # The user decides to delete the comment
    # Only comments by that user have delete buttons
    with pytest.raises(NoSuchElementException):
        comments[0].delete()
    # User clicks the delete button
    comments[3].delete()

    # The comment is now gone
    assert len(post_page.comments) == 3
