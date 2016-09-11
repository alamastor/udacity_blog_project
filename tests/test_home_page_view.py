from collections import namedtuple
from datetime import datetime

from bs4 import BeautifulSoup
import pytest

from views_base import testapp


@pytest.fixture
def mock_BlogPost_fetch(mocker):
    BlogPost = namedtuple('BlogPost', ['title', 'content', 'datetime', 'key'])
    mocked_query = mocker.patch('blog.views.BlogPost.query')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    keyId2 = mocker.Mock()
    keyId2.id = mocker.Mock(return_value=2)
    mocked_query.return_value.fetch.return_value = [
        BlogPost('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1),
        BlogPost('Post 2', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 11), keyId2),
    ]


def test_home_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_home_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body


def test_home_page_shows_blog_posts(testapp, mock_BlogPost_fetch):
    body = testapp.get('/').normal_body
    assert 'Post 1' in body
    assert 'Post 2' in body
    assert body.count('post__content') == 2


def test_home_page_post_are_order_newest_to_oldest(testapp, mock_BlogPost_fetch):
    body = testapp.get('/').normal_body
    soup = BeautifulSoup(body, 'html.parser')
    titles = [x.text for x in soup.find_all('h2', {'class': 'post__title'})]
    assert titles == ['Post 2', 'Post 1']


def test_home_has_links_to_individual_posts(testapp, mock_BlogPost_fetch):
    body = testapp.get('/').normal_body
    soup = BeautifulSoup(body, 'html.parser')
    links = [x.a['href'] for x in soup.find_all('h2', {'class': 'post__title'})]
    assert links == ['/post/2', '/post/1']
