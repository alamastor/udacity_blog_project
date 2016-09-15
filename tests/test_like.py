from collections import namedtuple
from datetime import datetime

from bs4 import BeautifulSoup
import pytest
from webtest import AppError

import views_base
from views_base import (
    testapp, fake_user, mock_BlogPost, mock_comments, mock_Like
)


def test_post_page_has_like_button(
    testapp, mock_BlogPost, mock_comments, mock_Like
):
    response = testapp.get('/post/%i' % mock_BlogPost.key.id())
    soup = BeautifulSoup(response.normal_body, 'html.parser')
    assert soup.find(class_='post__like')


def test_post_page_logged_in_as_creator_has_no_like_button(
    mocker, testapp, mock_comments, fake_user, mock_Like
):
    mock_blog_post = mock_BlogPost(mocker, user_id=fake_user.key.id())
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_blog_post.key.id(),
        fake_user.key.id()
    )
    soup = BeautifulSoup(response.normal_body, 'html.parser')
    assert not soup.find(class_='post__like')


def test_post_page_show_number_of_likes_if_user_has_liked(
    mocker, testapp, mock_BlogPost, mock_comments, fake_user
):
    user_id = fake_user.key.id()
    Like = namedtuple('Like', ['user_id', 'datetime'])
    mock_Like = mocker.patch('blog.views.Like', autospec=True)
    mock_Like.get_by_blog_post_id.return_value = [
        Like(user_id, datetime.now()),
        Like(11, datetime.now()),
        Like(12, datetime.now())
    ]

    response = views_base.logged_in_get_post_page(
        testapp,
        mock_BlogPost.key.id(),
        fake_user.key.id()
    )
    soup = BeautifulSoup(response.normal_body, 'html.parser')
    assert soup.find(class_='post__likes').text == '3 Likes'


def test_post_page_show_number_of_likes_if_user_is_creator(
    mocker, testapp, mock_comments, fake_user
):
    mock_blog_post = mock_BlogPost(mocker, user_id=fake_user.key.id())

    Like = namedtuple('Like', ['user_id', 'datetime'])
    mock_Like = mocker.patch('blog.views.Like', autospec=True)
    mock_Like.get_by_blog_post_id.return_value = [
        Like(10, datetime.now()),
        Like(11, datetime.now()),
        Like(12, datetime.now())
    ]
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_blog_post.key.id(),
        fake_user.key.id()
    )
    soup = BeautifulSoup(response.normal_body, 'html.parser')
    assert soup.find(class_='post__likes').text == '3 Likes'


def test_post_like_logged_out_redirects_to_login(testapp, mock_BlogPost):
    response = testapp.post('/post/%i' % mock_BlogPost.key.id(), {
        'like': 'like'
    })
    assert response.status_int == 302
    assert response.location.split('/')[-1] == 'login'


def test_post_like_as_blog_post_creator_returns_403(
    mocker, testapp, mock_comments, fake_user, mock_Like
):
    mock_blog_post = mock_BlogPost(mocker, user_id=fake_user.key.id())
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(
            testapp,
            '/post/%i' % mock_blog_post.key.id(),
            fake_user.key.id(),
            {'like': 'like'}
        )
    assert '403' in str(excinfo.value)


def test_logged_in_post_like_returns_200(
    mocker, testapp, mock_comments, fake_user, mock_Like, mock_BlogPost
):
    response = views_base.logged_in_post(
        testapp,
        '/post/%i' % mock_BlogPost.key.id(),
        fake_user.key.id(),
        {'like': 'like'}
    )
    assert response.status_int == 200


def test_logged_in_post_like_calls_Like_and_put(
    mocker, testapp, mock_comments, fake_user, mock_Like, mock_BlogPost
):
    views_base.logged_in_post(
        testapp,
        '/post/%i' % mock_BlogPost.key.id(),
        fake_user.key.id(),
        {'like': 'like'}
    )

    mock_Like.assert_called_once_with(
        user_id=fake_user.key.id(),
        parent=mock_BlogPost.key
    )
    mock_Like.return_value.put.assert_called_once()


def test_redirect_to_login_sets_after_login_cookie(testapp, mock_BlogPost):
    response = testapp.post('/post/%i' % mock_BlogPost.key.id(), {
        'like': 'like'
    })

    cookie_added = False
    for cookie in response.headers.getall('Set-Cookie'):
        cookie_name = cookie.split(';')[0].split('=')[0]
        cookie_val = cookie.split(';')[0].split('=')[1]
        if cookie_name == 'after_login':
            assert cookie_val == '"http://localhost/post/%i"' % mock_BlogPost.key.id()
            cookie_added = True
    assert cookie_added
