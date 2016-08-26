import pytest
import webtest
import webapp2

from blog.main import ROUTER


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


