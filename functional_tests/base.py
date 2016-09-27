from collections import namedtuple
from datetime import datetime
import random

import pytest
import requests
from bs4 import BeautifulSoup

from blog import auth

MAIN_PAGE_URL = 'http://localhost:8080'


@pytest.fixture
def browser():
    from selenium import webdriver
    browser = webdriver.Chrome()
    browser.implicitly_wait(2)
    yield browser

    browser.quit()


@pytest.fixture
def run_app():
    import subprocess
    app_proc = subprocess.Popen([
        'dev_appserver.py',
        '--clear_datastore=yes',
        '--datastore_path=/tmp/temp_blog_datastore',
        '--threadsafe_override=false',
        '--max_module_instances=1',
        'blog'
    ])
    yield

    app_proc.terminate()
    app_proc.wait()


def create_test_user(username=None, password=None, email=None):
    if not username:
        username = 'random_user_%i' % random.randint(0, 100000)
    if not password:
        password = str(random.randint(0, 100000))
    if not email:
        email = '%i@%i.com' % (random.randint(0, 100000), random.randint(0, 100000))
    res = requests.post('%s/signup' % MAIN_PAGE_URL, {
        'username': username,
        'password': password,
        'verify': password,
        'email': email
    })

    user_id = int(res.request.headers['Cookie'].split('=')[1].split('|')[0])
    User = namedtuple('User', ['username', 'password', 'email', 'user_id'])
    return User(username, password, email, user_id)


def create_test_blog_post(title, content, user_id=None):
    if not user_id:
        user_id = create_test_user().user_id
    auth_cookie = {'sess': '%i|%s' % (user_id, auth.make_secure_val(user_id))}

    res = requests.post('%s/post' % MAIN_PAGE_URL, {
        'title': title, 'content': content
    }, cookies=auth_cookie)

    return int(res.url.split('/')[-1])


def create_test_comment(post_id, comment, user_id=None):
    if not user_id:
        user_id = create_test_user().user_id

    auth_cookie = {'sess': '%i|%s' % (user_id, auth.make_secure_val(user_id))}

    res= requests.post('%s/post/%i/comment' % (MAIN_PAGE_URL, post_id), {
        'comment': comment
    }, cookies=auth_cookie)
