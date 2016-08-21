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


def test_Post_has_correct_fields():
    assert 'title' in Post._properties
    assert 'content' in Post._properties
    assert 'datetime' in Post._properties
    assert len(Post._properties) == 3


def test_User_has_correct_fields():
    assert 'username' in User._properties
    assert 'pw_hash' in User._properties
    assert 'salt' in User._properties
    assert len(User._properties) == 3


def test_User_query_by_username(testdb):
    user1 = User(username='asdf', pw_hash='asdf', salt='asdf')
    user1.put()
    user2 = User(username='qwer', pw_hash='qwer', salt='qwer')
    user2.put()

    assert User.get_by_username(user1.username) == user1

