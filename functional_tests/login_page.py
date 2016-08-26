import base


class LoginPage(object):

    def __init__(self, browser):
        self.browser = browser

    def go_to_login_page(self):
        self.browser.get(base.MAIN_PAGE_URL + '/signup')

    def submit_form(self, username, password, verify, email=''):
        username_input = self.browser.find_element_by_name('username')
        password_input = self.browser.find_element_by_name('password')
        verify_input = self.browser.find_element_by_name('verify')
        email_input = self.browser.find_element_by_name('email')
        submit = self.browser.find_element_by_xpath('//input[@type="submit"]')

        username_input.send_keys(username)
        password_input.send_keys(password)
        verify_input.send_keys(verify)
        email_input.send_keys(email)

        submit.click()

    def get_error_message(self):
        return self.browser.find_element_by_class_name('error').text
