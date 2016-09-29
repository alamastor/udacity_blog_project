from collections import namedtuple
from datetime import datetime

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
    assert response.html.find(class_='post__like')


def test_post_page_logged_in_as_creator_has_no_like_button(
    mocker, testapp, mock_comments, fake_user, mock_Like
):
    mock_blog_post = mock_BlogPost(mocker, user_id=fake_user.key.id())
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_blog_post.key.id(),
        fake_user.key.id()
    )
    assert not response.html.find(class_='post__like')


def test_post_page_show_number_of_likes_and_unlike_if_user_has_liked(
    mocker, testapp, mock_BlogPost, mock_comments, fake_user
):
    user_id = fake_user.key.id()
    Like = namedtuple('Like', ['user_id', 'datetime'])
    mock_Like = mocker.patch('views.views.Like', autospec=True)
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
    assert response.html.find(class_='post__likes').text == '3 Likes'
    assert response.html.find(class_='post__unlike')


def test_post_page_show_number_of_likes_if_user_is_creator(
    mocker, testapp, mock_comments, fake_user
):
    mock_blog_post = mock_BlogPost(mocker, user_id=fake_user.key.id())

    Like = namedtuple('Like', ['user_id', 'datetime'])
    mock_Like = mocker.patch('views.views.Like', autospec=True)
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
    assert response.html.find(class_='post__likes').text == '3 Likes'


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


def test_unlike_calls_Like_and_delete(
    mocker, testapp, mock_comments, fake_user, mock_Like, mock_BlogPost
):
    mock_already_liked = mocker.patch(
        'views.views.BlogPostPage.already_liked_blog_post', new_callable=mocker.PropertyMock
    )
    mock_already_liked.return_value = True

    views_base.logged_in_post(
        testapp,
        '/post/%i' % mock_BlogPost.key.id(),
        fake_user.key.id(),
        {'like': 'unlike'}
    )

    mock_Like.get_by_blog_post_id_and_user_id.assert_called_once_with(
        mock_BlogPost.key.id(),
        fake_user.key.id(),
    )
    mock_Like.get_by_blog_post_id_and_user_id.return_value.key.delete.assert_called_once()


def test_cannont_like_twice(
    mocker, testapp, mock_comments, fake_user, mock_Like, mock_BlogPost
):
    mock_already_liked = mocker.patch(
        'views.views.BlogPostPage.already_liked_blog_post', new_callable=mocker.PropertyMock
    )
    mock_already_liked.return_value = True

    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(
            testapp,
            '/post/%i' % mock_BlogPost.key.id(),
            fake_user.key.id(),
            {'like': 'like'}
        )
    assert '403' in str(excinfo.value)


def test_cannont_unlike_if_not_liked(
    mocker, testapp, mock_comments, fake_user, mock_Like, mock_BlogPost
):
    with pytest.raises(AppError) as excinfo:
        res = views_base.logged_in_post(
            testapp,
            '/post/%i' % mock_BlogPost.key.id(),
            fake_user.key.id(),
            {'like': 'unlike'}
        )
    assert '403' in str(excinfo.value)
