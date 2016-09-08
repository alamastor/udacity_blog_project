import pytest

from datetime import datetime

from blog.models import Post, User, Comment


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


def test_Comment_get_by_post_key(testdb):
    post_1 = Post(title='asd', content='asdf', datetime=datetime.now())
    post_1.put()
    post_2 = Post(title='asdfl', content='asdfx', datetime=datetime.now())
    post_2.put()
    comment1 = Comment(
        parent=post_1.key, comment='asdf', user_id=1, datetime=datetime.now()
    )
    comment1.put()
    comment2 = Comment(
        parent=post_2.key, comment='abc', user_id=1, datetime=datetime.now()
    )
    comment2.put()
    comment3 = Comment(
        parent=post_2.key, comment='qwe', user_id=5, datetime=datetime.now()
    )
    comment3.put()

    assert Comment.get_by_post_key(post_2.key) == [comment2, comment3]


def test_Comment_formatted_date(testdb):
    comment = Comment(comment='asdf', user_id=1, datetime=datetime(2015, 2, 1))

    assert comment.formatted_date == '1-Feb-2015'


def test_Comment_get_by_id_and_post_id(testdb):
    post = Post(title='asd', content='asdf', datetime=datetime.now())
    post.put()
    comment = Comment(
        parent=post.key, comment='asdf', user_id=1, datetime=datetime.now()
    )
    comment.put()

    assert Comment.get_by_id_and_post_id(comment.key.id(), post.key.id()) == comment
