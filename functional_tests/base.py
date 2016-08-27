import pytest
import requests
from bs4 import BeautifulSoup

MAIN_PAGE_URL = 'localhost:8080'
DATASTORE_URL = 'http://localhost:8000/datastore'


@pytest.fixture
def browser():
    from selenium import webdriver
    browser = webdriver.Firefox()
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


def write_to_db(entity_kind, fields):
    page = requests.get('%s?edit=%s' % (DATASTORE_URL, entity_kind))
    soup = BeautifulSoup(page.content, 'html.parser')
    xsrf_token = soup.find('input', {'name': 'xsrf_token'})['value']
    post_data = {
        'kind': entity_kind,
        'xsrf_token': xsrf_token
    }
    for field in fields:
        post_data['%s|%s' % (field.type, field.name)] = field.value
    requests.post(DATASTORE_URL + '/edit', data=post_data)