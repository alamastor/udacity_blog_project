from collections import namedtuple
from datetime import datetime

from bs4 import BeautifulSoup
import pytest

from views_base import testapp


@pytest.fixture
def mock_BlogPost_query(mocker):
    BlogPost = namedtuple('BlogPost', ['title', 'content', 'datetime', 'key'])
    mocked_query = mocker.patch('blog.views.BlogPost.query')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    keyId2 = mocker.Mock()
    keyId2.id = mocker.Mock(return_value=2)
    mocked_query.return_value.fetch.return_value = [
        BlogPost('Post 2', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 11), keyId2),
        BlogPost('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1),
    ]
    mocked_query.return_value.iter.return_value.has_next.return_value = True
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
    body = testapp.get('/').normal_body
    soup = BeautifulSoup(body, 'html.parser')
    links = [x.a['href'] for x in soup.find_all('h2', {'class': 'post__title'})]
    assert links == ['/post/2', '/post/1']


def test_home_page_shows_link_to_next_page_if_more_posts_are_available(
    testapp, mock_BlogPost_query
):
    body = testapp.get('/').normal_body
    assert 'next-page' in body


def test_does_not_show_next_page_link_if_no_more_posts_are_available(
    testapp, mock_BlogPost_query
):
    mock_BlogPost_query.return_value.iter.return_value.has_next.return_value = False
    body = testapp.get('/').normal_body
    assert 'next-page' not in body


def test_next_page_button_has_value_of_next_page(
    testapp, mock_BlogPost_query
):
    soup = testapp.get('/', {'page': 2}).html
    assert int(soup.find(class_='next-page__button')['value']) == 3


def test_get_page_three_call_fetch_three_times(
    testapp, mock_BlogPost_query, mocker
):
    testapp.get('/', {'page': 3})
    assert mock_BlogPost_query.return_value.fetch.call_count == 3
