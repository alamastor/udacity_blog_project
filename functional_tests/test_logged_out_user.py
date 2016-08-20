import pytest

MAIN_PAGE_URL = 'localhost:8080'

@pytest.fixture
def browser():
    from selenium import webdriver
    browser = webdriver.Firefox()
    yield browser

    browser.quit()


@pytest.fixture
def run_app():
    import subprocess
    app_proc = subprocess.Popen(['dev_appserver.py', 'blog'])
    yield

    app_proc.terminate()


def test_user_can_view_posts(run_app, browser):
    # User visits main page.
    browser.get(MAIN_PAGE_URL)

    # User can see header and and mulitple posts.
    header_text = browser.find_element_by_tag_name('h1').text
    assert header_text == 'Bloggity'

    # User visits an individual blog post and can see content.
    assert 0
    # User write comment on blog post.

    # Comment is now visible on page.
