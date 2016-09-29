from collections import namedtuple
from datetime import datetime

import pytest

from views_base import testapp


@pytest.fixture
def mock_BlogPost_query(mocker):
    BlogPost = namedtuple('BlogPost', ['title', 'content', 'datetime', 'key'])
    mocked_query = mocker.patch('blog.views.views.BlogPost.query')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    keyId2 = mocker.Mock()
    keyId2.id = mocker.Mock(return_value=2)
    mocked_query.return_value.order.return_value.fetch_page.return_value = ([
        BlogPost('Post 2', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 11), keyId2),
        BlogPost('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1),
    ], mocker.Mock, False)
    return mocked_query

@pytest.fixture
def mock_BlogPost_query_many_posts(mocker):
    BlogPost = namedtuple('BlogPost', ['title', 'content', 'datetime', 'key'])
    mocked_query = mocker.patch('blog.views.views.BlogPost.query')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    keyId2 = mocker.Mock()
    keyId2.id = mocker.Mock(return_value=2)
    mocked_next_cur = mocker.Mock()
    type(mocked_next_cur).urlsafe = mocker.Mock(return_value=1234)
    mocked_query.return_value.order.return_value.fetch_page.return_value = ([
        BlogPost('Post 2', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 11), keyId2),
        BlogPost('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1),
    ] * 5, mocked_next_cur, True)
    return mocked_query


def test_home_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_home_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body


def test_home_page_shows_blog_posts(testapp, mock_BlogPost_query):
    body = testapp.get('/').normal_body
    assert 'Post 1' in body
    assert 'Post 2' in body
    assert body.count('post__content') == 2


def test_home_page_post_calls_query_order(testapp, mock_BlogPost_query):
    body = testapp.get('/').normal_body
    mock_BlogPost_query.return_value.order.assert_called_once()


def test_home_has_links_to_individual_posts(testapp, mock_BlogPost_query):
    soup = testapp.get('/').html
    links = [x.a['href'] for x in soup.find_all('h2', {'class': 'post__title'})]
    assert links == ['/post/2', '/post/1']


def test_home_page_shows_link_to_next_page_if_more_posts_are_available(
    testapp, mock_BlogPost_query_many_posts
):
    body = testapp.get('/').normal_body
    assert 'next-page' in body


def test_does_not_show_next_page_link_if_no_more_posts_are_available(
    testapp, mock_BlogPost_query
):
    mock_BlogPost_query.return_value.iter.return_value.has_next.return_value = False
    body = testapp.get('/').normal_body
    assert 'next-page' not in body
