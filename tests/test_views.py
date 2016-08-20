import pytest

from blog.main import HomePage


@pytest.fixture
def testapp():
    import webapp2
    import webtest
    from blog.main import ROUTER
    app = webapp2.WSGIApplication(ROUTER)
    return webtest.TestApp(app)


def test_main_page_returns_200(testapp):
    assert testapp.get('/').status_int == 200


def test_main_page_shows_header(testapp):
    assert 'Bloggity' in testapp.get('/').normal_body
