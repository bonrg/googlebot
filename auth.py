from selenium import webdriver
import pickle, requests, os, time
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from requests.exceptions import RequestException
from logging import getLogger


logger = getLogger('Checkers')


class GoogleBotError(Exception):
    pass


class GoogleBot:

    WEBDRIVERPATH = '{your_path_to_webfriver}/chromedriver_75'
    ACCOUNT_GOOGLE_ELEMENTS = {
        'input_login': 'Email',
        'input_password': 'Passwd',
        'nextButton': 'next',
        'signinButton': 'signIn',
        'check_is_logged': '//h1[@class="x7WrMb"]',
    }
    AUTH_URL = 'https://accounts.google.com/signin/v2/identifier?flowName=GlifWebSignIn&flowEntry=ServiceLogin'
    #  Cookies expire 3 months since the last modification

    def __init__(self, login: str, password: str):
        self.login = login
        self.password = password
        self.COOKIE_FILE = 'google_'+ self.login +'_cookies.pkl'

    def _get_cookies(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--test-type')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--no-default-browser-check')
        chrome_options.add_argument('--ignore-certificate-errors')
        chrome_options.add_argument('--start-maximized')

        try:
            browser = webdriver.Chrome(executable_path=self.WEBDRIVERPATH, options=chrome_options)
            requests.get(self.AUTH_URL)
            browser.get(self.AUTH_URL)
            browser.implicitly_wait(10)
            input_login = browser.find_element_by_id(self.ACCOUNT_GOOGLE_ELEMENTS.get('input_login', None))
            if input_login:
                input_login.send_keys(self.login)
                browser.find_element_by_id(self.ACCOUNT_GOOGLE_ELEMENTS.get('nextButton', None)).click()
                input_password = browser.find_element_by_id(self.ACCOUNT_GOOGLE_ELEMENTS.get('input_password', None))
                input_password.send_keys(self.password)
                browser.find_element_by_id(self.ACCOUNT_GOOGLE_ELEMENTS.get('signinButton', None)).click()
                browser.implicitly_wait(15)
                html_source = browser.page_source
                check_is_logged = browser.find_element_by_xpath(self.ACCOUNT_GOOGLE_ELEMENTS.get('check_is_logged', None))
                if check_is_logged:
                    google_cookies = browser.get_cookies()
                    cookies = ({cookie.get("name"): cookie.get("value") for cookie in google_cookies},
                               google_cookies[0].get("expiry"))
                    with open(self.COOKIE_FILE, "wb") as f:
                        pickle.dump(cookies, f)
                        browser.quit()
                    return cookies
        except RequestException as e:
            logger.warning(e)
            raise GoogleBotError('Google host not responding')
        except WebDriverException as e:
            print(html_source)
            logger.warning(e)
            raise GoogleBotError('Invalid login or password | Can not find the required google element of parsing')

    def load_cookies(self):
        try:
            check_file_exists = os.path.isfile(self.COOKIE_FILE)
            if check_file_exists:
                with open(self.COOKIE_FILE, 'rb') as f:
                    cookies, expiry = pickle.load(f)
                    if expiry < time.time():
                        cookies, expiry = self._get_cookies()
                return cookies
            else:
                cookies, expiry = self._get_cookies()
                return cookies
        except FileNotFoundError as e:
            logger.warning(f'Cookie file not found {e}')


login = ''
password = ''
bot = GoogleBot(login, password)
cookie = bot.load_cookies()

print(cookie)
