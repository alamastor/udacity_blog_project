import pytest

from datetime import datetime

from models.like import Like
from models.comment import Comment
from models.user import User
from models.blog_post import blog_key, BlogPost


@pytest.fixture
def testdb():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    testbed.init_datastore_v3_stub()
    testbed.init_memcache_stub()


def test_BlogPost_date_str(testdb):
    post = BlogPost(
        title='xz',
        content='asdf',
        datetime=datetime(2016, 5, 3, 13, 6, 33),
        user_id=1
    )
    assert post.date_str == '3-May-2016'


def test_Post_username(testdb):
    user = User(username='kate', pw_hash='asdf', salt='asdf')
    user.put()
    post = BlogPost(
        title='asd',
        content='asdfas',
        datetime=datetime(2015, 12, 12),
        user_id=user.key.id()
    )
    post.put()

    assert post.username == user.username


def test_User_query_by_username(testdb):
    user1 = User(username='asdf', pw_hash='asdf', salt='asdf')
    user1.put()
    user2 = User(username='qwer', pw_hash='qwer', salt='qwer')
    user2.put()

    assert User.get_by_username(user1.username).username == user1.username


def test_Comment_get_by_blog_post_key(testdb):
    blog_post_1 = BlogPost(
        parent=blog_key(),
        title='asd',
        content='asdf',
        datetime=datetime.now(),
        user_id=1
    )
    blog_post_1.put()
    blog_post_2 = BlogPost(
        parent=blog_key(),
        title='asdfl',
        content='asdfx',
        datetime=datetime.now(),
        user_id=1
    )
    blog_post_2.put()
    comment1 = Comment(
        parent=blog_post_1.key,
        comment='asdf',
        user_id=1,
        datetime=datetime.now()
    )
    comment1.put()
    comment2 = Comment(
        parent=blog_post_2.key,
        comment='abc',
        user_id=1,
        datetime=datetime.now()
    )
    comment2.put()
    comment3 = Comment(
        parent=blog_post_2.key,
        comment='qwe',
        user_id=5,
        datetime=datetime.now()
    )
    comment3.put()

    comments = Comment.get_by_blog_post_key(blog_post_2.key)
    assert comments == [comment2, comment3]


def test_Comment_formatted_date(testdb):
    comment = Comment(comment='asdf', user_id=1, datetime=datetime(2015, 2, 1))

    assert comment.formatted_date == '1-Feb-2015'


def test_Comment_get_by_id_and_blog_post_id(testdb):
    blog_post = BlogPost(
        parent=blog_key(),
        title='asd',
        content='asdf',
        datetime=datetime.now(),
        user_id=1
    )
    blog_post.put()
    comment = Comment(
        parent=blog_post.key, comment='asd', user_id=1, datetime=datetime.now()
    )
    comment.put()

    assert Comment.get_by_id_and_blog_post_key(
        comment.key.id(), blog_post.full_key
    ) == comment


def test_Comment_username(testdb):
    user = User(username='kate', pw_hash='asdf', salt='asdf')
    user.put()
    comment = Comment(
        comment='asdf',
        user_id=user.key.id(),
        datetime=datetime.now()
    )
    comment.put()

    assert comment.username == user.username


def test_Like_get_by_post_id(testdb):
    blog_post = BlogPost(
        parent=blog_key(),
        title='asd',
        content='asdf',
        datetime=datetime.now(),
        user_id=1
    )
    blog_post.put()

    like_1 = Like(parent=blog_post.key, user_id=1)
    like_1.put()
    like_2 = Like(parent=blog_post.key, user_id=2)
    like_2.put()

    result = Like.get_by_blog_post_id(blog_post.key.id())
    assert len(result) == 2
    assert like_1 in result
    assert like_2 in result


def test_like_get_by_post_id_and_user_id(testdb):
    blog_post = BlogPost(
        parent=blog_key(),
        title='asd',
        content='asdf',
        datetime=datetime.now(),
        user_id=1
    )
    blog_post.put()

    like_1 = Like(parent=blog_post.key, user_id=1)
    like_1.put()
    like_2 = Like(parent=blog_post.key, user_id=2)
    like_2.put()

    result = Like.get_by_blog_post_id_and_user_id(
        blog_post.key.id(), user_id=2
    )
    assert result == like_2
