from collections import namedtuple

import pytest

from pages import PostPage
import base
from base import run_app, browser


Field = namedtuple('Field', ['type', 'name', 'value'])

@pytest.fixture
def add_posts():
    base.write_to_db('Post', (
        Field('string', 'title', 'Post 1'),
        Field('Text', 'content', 'asdfasfklanwemfl;aknf'),
        Field('datetime', 'datetime', '2016-8-10 06:12:23')
    ))
    base.write_to_db('Post', (
        Field('string', 'title', 'Post 2'),
        Field('Text', 'content', 'asdfasfklanwemfl;aknf'),
        Field('datetime', 'datetime', '2016-8-11 06:12:23')
    ))


def test_post_page(run_app, browser, add_posts):
    post_id = base.write_to_db('Post', (
        Field('string', 'title', 'post title'),
        Field('Text', 'content', 'asdfasfklanwemfl;aknf'),
        Field('datetime', 'datetime', '2016-8-11 06:12:23')
    ))

    # User visit post page.
    post_page = PostPage(browser, post_id)
    post_page.visit_page()

    # Post is visible on page.
    assert post_page.title == 'post title'

    # Three comments are visible on the page.
    comments = post_page.comments
    assert len(comments) == 3

    # The first comment has the correct content.
    assert comments[0].content == 'COMMENT CONTENT'

    # The user is not logged in so warning is visible.
    login_message == browser.find_element_by_class_name('login-message').text
    assert login_message == 'You must be logged in to comment'
    # No comment box is visible.
    with pytest.raises(NoSuchElementException):
        browser.find_element_by_class_name('add-comment')

    # User logs in.
    login_page = LoginPage(browser)
    login_page.visit_page()
    test_user = base.create_test_user()
    login_page.submit_form(test_user.username, test_user.password)

    # User post a comment.
    post_page.visit_page()
    post_page.write_comment('A mediocre comment')

    # The comment is now visible on the page.
    comments = post_page.comments
    assert len(comments) == 4
    assert comments[3].content == 'A mediocre comment'

    # The user decides to edit the comment.
    # Only comments by that user have edit buttons
    with pytest.raises(NoSuchElementException):
        comments[0].write_update('')
    # The comment be edited.
    comments[4].write_update('A slightly better comment')

    # The updated comment is now visible on the page.
    comments = post_page.comments
    assert len(comments) == 4
    assert comments[3].content == 'A slightly better comment'

    # The user decides to delete the comment
    # Only comments by that user have delete buttons
    with pytest.raises(NoSuchElementException):
        comments[0].delete_button
    # User clicks the delete button
    comments[4].delete_button.click()

    # The comment is now gone
    assert len(post_page.comments) == 3
