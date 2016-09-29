import pytest
from webtest import AppError

import views_base
from views_base import (
    testapp, fake_user, mock_BlogPost, mock_comments, mock_Like
)


def test_view_blog_post_as_different_user_has_no_edit_link(
    testapp, mock_BlogPost, fake_user, mock_comments, mock_Like
):
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_BlogPost.key.id(),
        fake_user.key.id()
    )
    soup = response.html
    assert not soup.find(class_='post__edit')


def test_view_blog_post_as_same_user_has_edit_link(
    testapp, mocker, fake_user, mock_comments, mock_Like
):
    mock_post = mock_BlogPost(mocker, user_id=fake_user.key.id())
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_post.key.id(),
        fake_user.key.id()
    )
    soup = response.html
    assert soup.find(class_='post__edit')


def test_get_noexistant_post_edit_page_returns_404(
    testapp, mocker, fake_user
):
    mock_BlogPost = mocker.patch('blog.views.views.BlogPost')
    mock_BlogPost.get_by_id.return_value = None
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_get(
            testapp, '/post/%i/edit' % 123, fake_user.key.id()
        )
    assert '404' in str(excinfo.value)


def test_get_post_edit_page_redirects_to_login_if_not_logged_in(
    testapp, mock_BlogPost
):
    response = testapp.get('/post/%i/edit' % mock_BlogPost.key.id())
    assert response.status_int == 302
    assert response.location.split('/')[-1] == 'login'


def test_get_post_edit_page_return_403_if_logged_in_as_different_user(
    testapp, mock_BlogPost, fake_user
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_get(testapp, '/post/%i/edit' % post_id, user_id)
    assert '403' in str(excinfo.value)


def test_get_post_post_edit_page_return_200_if_logged_in_as_same_user(
    testapp, fake_user, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost(mocker, user_id).key.id()

    response = views_base.logged_in_get(testapp, '/post/%i/edit' % post_id, user_id)
    assert response.status_int == 200


def test_authorized_get_post_id_shows_edit_boxes_with_prefilled_vals(
    testapp, fake_user, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost(mocker, user_id).key.id()
    response = views_base.logged_in_get(testapp, '/post/%i/edit' % post_id, user_id)

    soup = response.html

    # Text values from mocked_BlogPost in views_base
    assert soup.find(class_='post-form__post-title')['value'] == 'Post 1'
    assert soup.find(
        class_='post-form__post-content'
    ).text == 'dfjals;dfjawpoefinasdni'


def test_post_to_post_edit_page_redirects_to_login_if_not_logged_in(
    testapp, mock_BlogPost
):
    response = testapp.post('/post/%i' % mock_BlogPost.key.id())
    assert response.status_int == 302
    assert response.location.split('/')[-1] == 'login'


def test_post_to_noexistant_post_edit_page_return_404(
    testapp, mocker, fake_user
):
    mock_BlogPost = mocker.patch('blog.views.views.BlogPost')
    mock_BlogPost.get_by_id.return_value = None
    user_id = fake_user.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(testapp, '/post/%i' % 1234, user_id)
    assert '404' in str(excinfo.value)


def test_post_to_post_edit_page_return_403_if_logged_in_as_different_user(
    testapp, mock_BlogPost, fake_user
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(testapp, '/post/%i' % post_id, user_id)
    assert '403' in str(excinfo.value)

def test_post_to_post_edit_page_calls_put(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_BlogPost(mocker, user_id)
    post_id = mock_post.key.id()
    views_base.logged_in_post(testapp, '/post/%i' % post_id, user_id, {
        'title': 'new title', 'content': 'new content'
    })

    mock_post.put.assert_called_once()


def test_post_with_invalid_title_shows_error(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_BlogPost(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i' % post_id,
        user_id,
        {'title': 'zx', 'content': 'asdfasdf afdsasdfasdf asdfadsf'}
    )
    assert 'Invalid title' in response.normal_body


def test_post_with_invalid_content_shows_error(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_BlogPost(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i' % post_id,
        user_id,
        {'title': 'zxasdfas', 'content': 'asd'}
    )
    assert 'Invalid content' in response.normal_body


def test_valid_post_redirects_to_post_page(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_BlogPost(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i' % post_id,
        user_id,
        {'title': 'new title', 'content': 'new content'}
    )
    assert response.status_int == 302
    assert response.location.split('/')[-2:] == ['post', '1']


def test_view_blog_post_as_different_user_has_no_delete_button(
    testapp, mock_BlogPost, fake_user, mock_comments, mock_Like
):
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_BlogPost.key.id(),
        fake_user.key.id()
    )
    soup = response.html
    assert not soup.find(class_='post__delete')


def test_view_blog_post_as_same_user_has_delete_button(
    testapp, mocker, fake_user, mock_comments, mock_Like
):
    mock_post = mock_BlogPost(mocker, user_id=fake_user.key.id())
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_post.key.id(),
        fake_user.key.id()
    )
    soup = response.html
    assert soup.find(class_='post__delete')


def test_post_delete_redirects_to_login_if_not_logged_in(
    testapp, mock_BlogPost
):
    response = testapp.post('/post/%i' % mock_BlogPost.key.id(), {
        'delete': 'delete'
    })
    assert response.status_int == 302
    assert response.location.split('/')[-1] == 'login'


def test_post_delete_to_nonexistant_post_returns_404(
    testapp, mocker, fake_user
):
    mock_BlogPost = mocker.patch('blog.views.views.BlogPost')
    mock_BlogPost.get_by_id.return_value = None
    user_id = fake_user.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(testapp, '/post/%i' % 123, user_id, {
            'delete': 'delete'
        })
    assert '404' in str(excinfo.value)


def test_post_delete_returns_403_if_logged_in_as_different_user(
    testapp, mock_BlogPost, fake_user
):
    user_id = fake_user.key.id()
    post_id = mock_BlogPost.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(testapp, '/post/%i' % post_id, user_id, {
            'delete': 'delete'
        })
    assert '403' in str(excinfo.value)


def test_post_delete_calls_delete(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_BlogPost(mocker, user_id)
    post_id = mock_post.key.id()
    views_base.logged_in_post(testapp, '/post/%i' % post_id, user_id, {
        'delete': 'delete'
    })

    mock_post.key.delete.assert_called_once()


def test_valid_post_delete_redirects_to_home_page(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_BlogPost(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i' % post_id,
        user_id,
        {'delete': 'delete'}
    )
    assert response.status_int == 302
    assert response.location == 'http://localhost/'


def test_redirect_from_create_set_correctly_sets_cookie(testapp):
    res = testapp.get(
        '/post/create'
    )

    assert views_base.cookie_set(res, 'after_login', '"http://localhost/post/create"')
