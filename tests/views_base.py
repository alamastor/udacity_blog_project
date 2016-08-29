import pytest
import webtest
import webapp2

from blog.main import ROUTER
from blog.models import User


@pytest.fixture
def testapp():
    from google.appengine.ext import testbed
    testbed = testbed.Testbed()
    testbed.activate()
    testbed.init_app_identity_stub()
    testbed.init_datastore_v3_stub()
    testbed.init_memcache_stub()
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


@pytest.fixture
def fake_user():
    user = User(
        username='Billy_Bob',
        pw_hash='ea6b636e740f821220fe50263f127519a5185fe875df414bbe6b00de21a5b281',
        salt='12345678'
    )
    user.put()
    return user
