from collections import namedtuple
from datetime import datetime

import pytest
import webtest

from views_base import testapp


@pytest.fixture
def mock_Post_get_by_id(mocker):
    Post = namedtuple('Post', ['title', 'content', 'datetime', 'key'])
    mocked_get = mocker.patch('blog.views.Post.get_by_id')
    keyId1 = mocker.Mock()
    keyId1.id = mocker.Mock(return_value=1)
    mocked_get.return_value = Post('Post 1', 'dfjals;dfjawpoefinasdni', datetime(2016, 8, 10), keyId1)


def test_get_post_returns_404_if_post_does_not_exist(testapp):
    with pytest.raises(webtest.AppError) as e:
        testapp.get('/posts/asdfadsfadsf')
        assert '404' in e.value


def test_get_post_returns_200_if_post_exists(testapp, mock_Post_get_by_id):
    assert testapp.get('/post/1').status_int == 200
