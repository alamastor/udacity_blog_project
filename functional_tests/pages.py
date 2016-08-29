import base


class Page(object):
    def __init__(self, browser, url):
        self.browser = browser
        self.url = url

    def visit_page(self):
        self.browser.get(self.url)


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
        super(CreatePage, self).__init__(browser, base.MAIN_PAGE_URL + '/create')

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
