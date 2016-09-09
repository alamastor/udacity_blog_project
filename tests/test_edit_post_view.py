from bs4 import BeautifulSoup
import pytest
from webtest import AppError

import views_base
from views_base import testapp, fake_user, mock_Post, mock_comments


def test_view_blog_post_as_different_user_has_no_edit_link(
    testapp, mock_Post, fake_user, mock_comments
):
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_Post.key.id(),
        fake_user.key.id()
    )
    soup = BeautifulSoup(response.normal_body, 'html.parser')
    assert not soup.find(class_='post__edit')


def test_view_blog_post_as_same_user_has_edit_link(
    testapp, mocker, fake_user, mock_comments
):
    mock_post = mock_Post(mocker, user_id=fake_user.key.id())
    response = views_base.logged_in_get_post_page(
        testapp,
        mock_post.key.id(),
        fake_user.key.id()
    )
    soup = BeautifulSoup(response.normal_body, 'html.parser')
    assert soup.find(class_='post__edit')


def test_get_noexistant_post_edit_page_return_404(
    testapp, mocker
):
    mock_Post = mocker.patch('blog.views.Post')
    mock_Post.get_by_id.return_value = None
    with pytest.raises(AppError) as excinfo:
        testapp.get('/post/%i/edit' % 123)
    assert '404' in str(excinfo.value)


def test_get_post_edit_page_return_401_if_not_logged_in(
    testapp, mock_Post
):
    with pytest.raises(AppError) as excinfo:
        testapp.get('/post/%i/edit' % mock_Post.key.id())
    assert '401' in str(excinfo.value)


def test_get_post_edit_page_return_401_if_logged_in_as_different_user(
    testapp, mock_Post, fake_user
):
    user_id = fake_user.key.id()
    post_id = mock_Post.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_get(testapp, '/post/%i/edit' % post_id, user_id)
    assert '401' in str(excinfo.value)


def test_get_post_post_edit_page_return_200_if_logged_in_as_same_user(
    testapp, fake_user, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_Post(mocker, user_id).key.id()

    response = views_base.logged_in_get(testapp, '/post/%i/edit' % post_id, user_id)
    assert response.status_int == 200


def test_authorized_get_post_id_shows_edit_boxes_with_prefilled_vals(
    testapp, fake_user, mocker
):
    user_id = fake_user.key.id()
    post_id = mock_Post(mocker, user_id).key.id()
    response = views_base.logged_in_get(testapp, '/post/%i/edit' % post_id, user_id)

    soup = BeautifulSoup(response.normal_body, 'html.parser')

    # Text values from mocked_Post in views_base
    assert soup.find(class_='post-form__post-title')['value'] == 'Post 1'
    assert soup.find(
        class_='post-form__post-content'
    ).text == 'dfjals;dfjawpoefinasdni'


def test_post_to_noexistant_post_edit_page_return_404(
    testapp, mocker
):
    mock_Post = mocker.patch('blog.views.Post')
    mock_Post.get_by_id.return_value = None
    with pytest.raises(AppError) as excinfo:
        testapp.post('/post/%i/edit' % 123)
    assert '404' in str(excinfo.value)


def test_post_to_post_edit_page_return_401_if_not_logged_in(
    testapp, mock_Post
):
    with pytest.raises(AppError) as excinfo:
        testapp.post('/post/%i/edit' % mock_Post.key.id())
    assert '401' in str(excinfo.value)


def test_post_to_post_edit_page_return_401_if_logged_in_as_different_user(
    testapp, mock_Post, fake_user
):
    user_id = fake_user.key.id()
    post_id = mock_Post.key.id()
    with pytest.raises(AppError) as excinfo:
        views_base.logged_in_post(testapp, '/post/%i/edit' % post_id, user_id)
    assert '401' in str(excinfo.value)

def test_post_to_post_edit_page_calls_put(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_Post(mocker, user_id)
    post_id = mock_post.key.id()
    views_base.logged_in_post(testapp, '/post/%i/edit' % post_id, user_id, {
        'title': 'new title', 'content': 'new content'
    })

    mock_post.put.assert_called_once()


def test_post_with_invalid_title_shows_error(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_Post(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i/edit' % post_id,
        user_id,
        {'title': 'zx', 'content': 'asdfasdf afdsasdfasdf asdfadsf'}
    )
    assert 'Invalid title' in response.normal_body


def test_post_with_invalid_content_shows_error(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_Post(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i/edit' % post_id,
        user_id,
        {'title': 'zxasdfas', 'content': 'asd'}
    )
    assert 'Invalid content' in response.normal_body


def test_valid_post_redirects_to_post_page(testapp, fake_user, mocker):
    user_id = fake_user.key.id()
    mock_post = mock_Post(mocker, user_id)
    post_id = mock_post.key.id()
    response = views_base.logged_in_post(
        testapp,
        '/post/%i/edit' % post_id,
        user_id,
        {'title': 'new title', 'content': 'new content'}
    )
    assert response.status_int == 302
    assert response.location.split('/')[-2:] == ['post', '1']