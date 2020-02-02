from selenium.webdriver import Firefox, FirefoxProfile
from selenium.webdriver.firefox.options import Options
import time

class FirefoxBrowser:
    """
    This is browser resource class for ObjectPool. This class demonstrate how to create resource class
    and implement methods described in the user guide section.
    """

    def __init__(self):
        self.browser = FirefoxBrowser.create_ff_browser()
        self.page_title = None

    @classmethod
    def create_ff_browser(cls):
        """Returns headless firefox browser object"""
        profile = FirefoxProfile().set_preference("intl.accept_languages", "es")
        opts = Options()
        opts.headless = True
        browser = Firefox(options=opts, firefox_profile=profile)
        return browser

    def get_page_title(self, url):
        """Returns page title of the url"""
        browser = self.browser
        browser.get(url)
        self.page_title = browser.title
        return self.page_title

    def clean_up(self, **stats):
        """quits browser and sets None, when this method is called"""
        self.browser.quit()
        self.browser = None

    def check_invalid(self, **stats):
        """Returns invalid=True if the browser accessed google web page, otherwise False"""
        if self.page_title == 'Google':
            return True
        return False
