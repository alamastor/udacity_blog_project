from collections import namedtuple
from datetime import datetime

import base


class Page(object):

    def __init__(self, browser, url):
        self.browser = browser
        self.url = url

    def visit_page(self):
        self.browser.get(self.url)
        return self

    def is_open(self):
        current_url = self.browser.current_url
        if current_url[-1] == '/':
            current_url = current_url[:-1]

        return current_url == self.url

    @property
    def login_button(self):
        return self.browser.find_element_by_class_name('login-button')


class HomePage(Page):

    def __init__(self, browser):
        super(HomePage, self).__init__(browser, base.MAIN_PAGE_URL)

    @property
    def blog_posts(self):
        post_eles = self.browser.find_elements_by_class_name('post')
        return [BlogPost(x) for x in post_eles]

    @property
    def create_blog_post_link(self):
        return self.browser.find_element_by_class_name('create-link')

    @property
    def header(self):
        return self.browser.find_element_by_tag_name('h1')


class BlogPost(object):

    def __init__(self, element):
        self.element = element

    @property
    def title(self):
        return self.element.find_element_by_class_name('post__title').text

    @property
    def post_id(self):
        return int(self.link.split('/')[-1])

    @property
    def link(self):
        header = self.element.find_element_by_class_name('post__title')
        link = header.find_element_by_tag_name('a')
        return str(link.get_attribute('href'))

    def click(self):
        header = self.element.find_element_by_class_name('post__title')
        link = header.find_element_by_tag_name('a')
        link.click()


class SignUpPage(Page):

    def __init__(self, browser):
        super(SignUpPage, self).__init__(browser, base.MAIN_PAGE_URL + '/signup')

    def submit_form(self, username, password, verify, email=''):
        username_input = self.browser.find_element_by_name('username')
        password_input = self.browser.find_element_by_name('password')
        verify_input = self.browser.find_element_by_name('verify')
        email_input = self.browser.find_element_by_name('email')
        submit = self.browser.find_element_by_xpath('//input[@type="submit"]')

        username_input.clear()
        password_input.clear()
        verify_input.clear()
        email_input.clear()

        username_input.send_keys(username)
        password_input.send_keys(password)
        verify_input.send_keys(verify)
        email_input.send_keys(email)

        submit.click()

    def get_error_message(self):
        return self.browser.find_element_by_class_name('error').text


class LoginPage(Page):

    def __init__(self, browser):
        super(LoginPage, self).__init__(browser, base.MAIN_PAGE_URL + '/login')

    def submit_form(self, username, password):
        user_input = self.browser.find_element_by_name('username')
        pw_input = self.browser.find_element_by_name('password')
        submit = self.browser.find_element_by_xpath('//input[@type="submit"]')

        user_input.clear()
        pw_input.clear()

        user_input.send_keys(username)
        pw_input.send_keys(password)
        submit.click()

    def get_error_message(self):
        return self.browser.find_element_by_class_name('error').text


class CreatePage(Page):

    def __init__(self, browser):
        super(CreatePage, self).__init__(browser, base.MAIN_PAGE_URL + '/post/create')

    def submit_form(self, title, content):
        title_input = self.browser.find_element_by_name('title')
        content_input = self.browser.find_element_by_name('content')
        submit = self.browser.find_element_by_xpath('//input[@type="submit"]')

        title_input.clear()
        content_input.clear()

        title_input.send_keys(title)
        content_input.send_keys(content)
        submit.click()

    def get_error_message(self):
        return self.browser.find_element_by_class_name('error').text


class BlogPostPage(Page):

    def __init__(self, browser, post_no):
        super(BlogPostPage, self).__init__(
            browser, '%s/post/%i' % (base.MAIN_PAGE_URL, post_no)
        )

    @property
    def home_link(self):
        return self.browser.find_element_by_class_name('home-link')

    @property
    def title(self):
        return self.browser.find_element_by_class_name('post__title').text

    @property
    def date(self):
        ele = self.browser.find_element_by_class_name('post__date')
        return datetime.strptime(ele.text, '%d-%b-%Y').date()

    @property
    def content(self):
        return self.browser.find_element_by_class_name('post__content').text

    def edit(self, title=None, content=None):
        edit_button = self.browser.find_element_by_class_name('post__edit')
        edit_button.click()

        if title:
            title_area = self.browser.find_element_by_class_name('post-form__post-title')
            title_area.clear()
            title_area.send_keys(title)

        if content:
            content_area = self.browser.find_element_by_class_name('post-form__post-content')
            content_area.clear()
            content_area.send_keys(content)

        submit_button = self.browser.find_element_by_class_name(
            'post-form__submit'
        )
        submit_button.click()

    def delete(self):
        delete_button = self.browser.find_element_by_class_name('post__delete')
        delete_button.click()

    @property
    def comments(self):
        comment_eles = self.browser.find_elements_by_class_name('comment')

        comments = []
        for ele in comment_eles:
            comments.append(Comment(self.browser, ele))
        return comments

    def write_comment(self, comment):
        comment_form = self.browser.find_element_by_class_name('comment-form')
        comment_form.find_element_by_name('comment').send_keys(comment)
        comment_form.find_element_by_class_name('comment-form__submit').click()

    @property
    def likes(self):
        ele = self.browser.find_element_by_class_name('post__likes')
        return int(ele.text.split()[0])

    def like(self):
        self.browser.find_element_by_class_name('post__like').click()


class Comment(object):

    def __init__(self, browser, element):
        self.browser = browser
        self.element = element
        self.comment = self.element.find_element_by_class_name(
            'comment__comment'
        ).text
        self.username = self.element.find_element_by_class_name(
            'comment__user'
        ).text
        self.datetime = datetime.strptime(
            self.element.find_element_by_class_name('comment__date').text,
            '%d-%b-%Y'
        )

    def edit(self, comment):
        edit_button = self.element.find_element_by_class_name('comment__edit')
        edit_button.click()

        edit_box = self.browser.find_element_by_class_name('comment-form__textarea')
        edit_box.clear()
        edit_box.send_keys(comment)

        submit_button = self.browser.find_element_by_class_name('comment-form__submit')
        submit_button.click()

    def delete(self):
        delete_button = self.element.find_element_by_class_name('delete')
        delete_button.click()
