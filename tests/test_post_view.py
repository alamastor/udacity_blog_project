from collections import namedtuple
from datetime import datetime

import pytest
import webtest
from webtest import AppError

import views_base
from views_base import (
    testapp, fake_user, mock_BlogPost, mock_comments, mock_Like
)
from blog.utils import auth


def mock_Comment(mocker, comment, user_id, comment_id=0):
    mock_Comment_post = mocker.patch(
        'views.blog_post_page.Comment', autospec=True
    )
    mock_Comment_comm = mocker.patch(
        'views.comment_page.Comment', autospec=True
    )
    key = mocker.Mock()
    key.id.return_value = comment_id
    mock_comment = mocker.Mock()
    type(mock_comment).comment = comment
    type(mock_comment).paragraphs = comment.split('\n')
    type(mock_comment).user_id = user_id
    type(mock_comment).datetime = datetime.now()
    type(mock_comment).key = key

    mock_Comment_post.get_by_id_and_blog_post_key.return_value = mock_comment
    mock_Comment_post.get_by_blog_post_key.return_value = [mock_comment]

    mock_Comment_comm.get_by_id_and_blog_post_key.return_value = mock_comment
    mock_Comment_comm.get_by_blog_post_key.return_value = [mock_comment]

    return mock_comment


def test_get_post_returns_404_if_post_does_not_exist(testapp):
    with pytest.raises(webtest.AppError) as e:
        testapp.get('/posts/asdfadsfadsf')
        assert '404' in e.value


def test_get_post_returns_200_if_post_exists(
    testapp, mock_BlogPost, mock_comments, mock_Like
):
    assert testapp.get('/post/%i' % mock_BlogPost.key.id()).status_int == 200


@pytest.fixture
def soup(testapp, mock_BlogPost, mock_comments, mock_Like):
    response = testapp.get('/post/%i' % mock_BlogPost.key.id())
    return response.html


@pytest.fixture
def soup_logged_in(
    testapp, fake_user, mock_BlogPost, mock_comments, mock_Like
):
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_BlogPost.key.id(),
        fake_user.key.id()
    )
    return response.html


@pytest.fixture
def comments(soup):
    return soup.find_all(class_='comment')


def test_post_view_show_comments(comments):
    assert len(comments) == 3
    paragraph = comments[0].find('p', class_='comment__comment')
    assert paragraph.text.strip() == 'A comment'


def test_comments_have_a_user_and_date(comments):
    comment = comments[0]
    assert comment.find(class_='comment__user').text == 'A user'
    assert comment.find(class_='comment__date').text == '1-Jan-2014'


def test_comments_are_in_chronological_order(comments):
    comment_dates = [
        x.find(class_='comment__date').text for x in comments
    ]
    assert comment_dates == ['1-Jan-2014', '2-Jan-2014', '1-Jan-2015']


def test_logged_out_user_cannot_comment(soup):
    login_message = soup.find(class_='login-message').text
    assert login_message == 'You must be logged in to comment.'
    assert len(soup.find_all(class_='comment-form')) == 0


def test_logged_in_user_can_comment(soup_logged_in):
    soup = soup_logged_in
    assert len(soup.find_all(class_='login-message')) == 0
    assert len(soup.find_all(class_='comment-form')) == 1


def test_post_comment_while_logged_out_returns_401(testapp, mock_BlogPost):
    with pytest.raises(AppError) as excinfo:
        testapp.post('/post/%i/comment' % mock_BlogPost.key.id())
    assert '401' in str(excinfo.value)


def logged_in_get_comment_page(
        testapp, post_id, user_id, comment_id=None, extra_environ=[]
    ):
    if comment_id:
        url = '/post/%i/comment/%i' % (post_id, comment_id)
    else:
        url = '/post/%i/comment' % post_id
    return testapp.get(url, headers={
        'Cookie': 'sess=%s|%s; Path=/' % (
            user_id, auth.make_secure_val(user_id)
        )
    }, extra_environ=extra_environ)


def logged_in_post_comment(
    testapp, post_id, user_id, comment, comment_id=None
):
    if comment_id:
        url = '/post/%i/comment/%i' % (post_id, comment_id)
    else:
        url = '/post/%i/comment' % post_id
    return views_base.logged_in_post(
        testapp, url, user_id, {'comment': comment}
    )


def test_post_comment_calls_Comment(
    testapp, fake_user, mock_BlogPost, mocker, mock
):
    mock_Comment = mocker.patch('views.comment_page.Comment', autospec=True)

    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    logged_in_post_comment(testapp, user_id, post_id, 'D comment')
    mock_Comment.assert_called_once_with(
        parent=mock_BlogPost.key,
        comment='D comment',
        user_id=user_id,
        datetime=mock.ANY
    )
    mock_Comment.return_value.put.assert_called_once()


def test_logged_in_post_comment_redirects_to_post(
    testapp, fake_user, mock_BlogPost, mocker
):
    mock_Comment = mocker.patch('views.comment_page.Comment', autospec=True)

    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    response = logged_in_post_comment(testapp, user_id, post_id, 'D comment')

    assert response.status_int == 302
    assert response.location.split('/')[-2:] == ['post', str(post_id)]


def test_post_empty_comment_shows_error(testapp, fake_user, mock_BlogPost):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    response = logged_in_post_comment(testapp, post_id, user_id, '')
    error_message = response.html.find(class_='error').text
    assert error_message == 'Comment cannot be empty.'


def test_get_comment_while_logged_out_return_401(testapp, mock_BlogPost):
    with pytest.raises(AppError) as excinfo:
        testapp.get('/post/%i/comment' % mock_BlogPost.key.id())
    assert '401' in str(excinfo.value)


def test_get_comment_while_logged_in_returns_200(
    testapp, fake_user, mock_BlogPost
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    response = logged_in_get_comment_page(testapp, user_id, post_id)
    assert response.status_int == 200


def test_get_comment_shows_textarea(testapp, fake_user, mock_BlogPost):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    response = logged_in_get_comment_page(testapp, user_id, post_id)

    assert len(response.html.find_all('textarea')) == 1


def test_get_comment_shows_textarea(testapp, fake_user, mock_BlogPost):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    response = logged_in_get_comment_page(testapp, user_id, post_id)

    assert len(response.html.find_all('textarea')) == 1


def test_get_comment_with_nonexistant_id_returns_404(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    mock_Comment = mocker.patch('views.comment_page.Comment', autospec=True)
    mock_Comment.get_by_id_and_blog_post_key.return_value = None
    with pytest.raises(AppError) as excinfo:
        response = logged_in_get_comment_page(testapp, user_id, post_id, 1)
    assert '404' in str(excinfo.value)


def test_get_comment_with_other_user_returns_403(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    blog_post_id = mock_BlogPost.key.id()

    mock_Comment(mocker, 'A comment', 123643)
    with pytest.raises(AppError) as excinfo:
        logged_in_get_comment_page(testapp, user_id, blog_post_id, 1)
    assert '403' in str(excinfo.value)


def test_get_comment_with_id_show_comment_in_textarea(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    comment = 'A comment'
    mock_Comment(mocker, comment, user_id, 12345)

    response = logged_in_get_comment_page(testapp, user_id, post_id, 12345)

    assert response.html.textarea.text == comment


def test_post_comment_with_id_with_other_user_returns_403(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    mock_Comment(mocker, 'A comment', 123643)
    with pytest.raises(AppError) as excinfo:
        response = logged_in_post_comment(testapp, user_id, post_id, 'asdf', 1)
    assert '403' in str(excinfo.value)


def test_post_comment_calls_put(testapp, fake_user, mock_BlogPost, mocker):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    mock_comment = mock_Comment(mocker, 'A comment', user_id, 12345)
    logged_in_post_comment(testapp, user_id, post_id, 'asdf', 12346)

    mock_comment.put.assert_called_once()


def test_comment_with_different_user_has_no_delete_button(
    testapp, fake_user, mock_BlogPost, mock_comments, soup_logged_in
):
    assert len(soup_logged_in.find_all(class_='delete')) == 0


def test_comment_with_same_user_has_delete_button(
    testapp, fake_user, mock_BlogPost, mocker, mock_Like
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    mock_Comment(mocker, 'C comment', user_id, 1234)

    response = views_base.logged_in_get_post_page(testapp, post_id, user_id)
    assert len(response.html.find_all(class_='comment__delete')) == 1


def logged_in_post_delete(testapp, post_id, comment_id, user_id):
    return views_base.logged_in_post(
        testapp,
        '/post/%i/comment/%i' % (post_id, comment_id),
        user_id,
        {'delete': 'delete'}
    )


def test_post_to_delete_with_other_user_returns_403(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    comment_id = 1234
    mock_Comment(mocker, 'C comment', 1234, comment_id=comment_id)

    with pytest.raises(AppError) as excinfo:
        logged_in_post_delete(testapp, post_id, comment_id, user_id)
    assert '403' in str(excinfo.value)


def test_post_to_delete_with_other_user_doesnt_call_delete(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    comment_id = 1234
    mock_comment = mock_Comment(
        mocker,
        'C comment',
        1234,
        comment_id=comment_id
    )

    with pytest.raises(AppError) as excinfo:
        response = logged_in_post_delete(testapp, post_id, comment_id, user_id)
        mock_comment.key.delete.assert_not_called()


def test_post_to_delete_with_same_user_call_delete(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    comment_id = 1234
    mock_comment = mock_Comment(
        mocker,
        'C comment',
        user_id,
        comment_id=comment_id
    )

    logged_in_post_delete(testapp, post_id, comment_id, user_id)

    mock_comment.key.delete.assert_called_once()


def test_post_to_delete_with_same_user_redirects_to_post(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    comment_id = 1234
    mock_comment = mock_Comment(
        mocker,
        'C comment',
        user_id,
        comment_id=comment_id
    )

    response = logged_in_post_delete(testapp, post_id, comment_id, user_id)

    assert response.status_int == 302
    assert response.location.split('/')[-2:] == ['post', str(post_id)]


def test_comment_cancel_redirects_to_referer(
    testapp, fake_user, mock_BlogPost, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()

    comment = 'A comment'
    mock_Comment(mocker, comment, user_id, 12345)

    html = logged_in_get_comment_page(
        testapp,
        user_id,
        post_id,
        12345,
        extra_environ={'HTTP_REFERER': '/asdf'}
    ).html
    assert html.find(class_='form-cancel')['href'] == '/asdf'
