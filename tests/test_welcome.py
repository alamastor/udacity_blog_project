import views_base
from views_base import testapp, fake_user


def test_welcome_page_redirects_login_if_not_logged_in(testapp):
    res = testapp.get('/welcome')
    assert res.status_int == 302
    assert res.location.split('/')[-1] == 'login'


def test_welcome_page_returns_200_if_logged_in(testapp, fake_user):
    user_id = fake_user.key.id()
    assert views_base.logged_in_get(testapp, '/welcome', user_id).status_int == 200


def test_welcome_page_shows_username(testapp, fake_user):
    user_id = fake_user.key.id()
    username = fake_user.username
    soup = views_base.logged_in_get(testapp, '/welcome', user_id).html
    assert soup.find(class_='welcome-header').text == 'Welcome %s!' % username


def test_continue_links_to_correct_page(testapp, fake_user):
    user_id = fake_user.key.id()
    username = fake_user.username
    testapp.set_cookie('after_login', '/asdf')
    soup = views_base.logged_in_get(testapp, '/welcome', user_id).html
    assert soup.find(class_='continue-link')['href'] == '/asdf'


def test_continue_links_to_home_if_cookie_not_set(testapp, fake_user):
    user_id = fake_user.key.id()
    username = fake_user.username
    soup = views_base.logged_in_get(testapp, '/welcome', user_id).html
    assert soup.find(class_='continue-link')['href'] == '/'


def test_continue_deletes_after_login_cookie(testapp, fake_user):
    user_id = fake_user.key.id()
    testapp.set_cookie('after_login', '/asdf')
    res = views_base.logged_in_get(testapp, '/welcome', user_id)
    assert res.headers['Set-Cookie'][:13] == 'after_login=;'
