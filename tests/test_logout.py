import views_base
from views_base import testapp


def test_post_to_logout_deletes_session_cookie(testapp):
    res = testapp.post('/logout')
    assert views_base.cookie_set(res, 'sess', '')


def test_post_to_logout_redirects_to_referer(testapp):
    res = testapp.post('/logout', extra_environ={'HTTP_REFERER': '/asdf'})
    assert res.status_int == 302
    assert res.location.split('/')[-1] == 'asdf'
