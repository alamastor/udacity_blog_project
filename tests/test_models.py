import pytest

from datetime import datetime

from blog.models import Post, User


@pytest.fixture
def testdb():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    testbed.init_datastore_v3_stub()
    testbed.init_memcache_stub()


def test_Post_date_str(testdb):
    post = Post(
        title='xz',
        content='asdf',
        datetime=datetime(2016, 5, 3, 13, 6, 33)
    )
    assert post.date_str == '03-May-2016'


def test_formatted_content_adds_br_to_Post_content(testdb):

    content=(
        'asdf asdfa sdf\n'
        'asdfasdf asdf asdf\n'
        'asdfasdf sdf'
    )
    post = Post(
        title='asd',
        content=content,
        datetime=datetime(2015, 12, 12)
    )
    assert post.formatted_content == (
        'asdf asdfa sdf<br>asdfasdf asdf asdf<br>asdfasdf sdf'
    )


def test_User_query_by_username(testdb):
    user1 = User(username='asdf', pw_hash='asdf', salt='asdf')
    user1.put()
    user2 = User(username='qwer', pw_hash='qwer', salt='qwer')
    user2.put()

    assert User.get_by_username(user1.username) == user1
