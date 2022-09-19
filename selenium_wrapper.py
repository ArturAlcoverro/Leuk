import traceback
from io import BytesIO
from threading import Lock

import numpy as np
from PIL import Image
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, \
    ElementClickInterceptedException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class SeleniumWrapper():
    """
    Selenium wrapper
    """

    # instance = None

    '''def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance'''

    def __init__(self, driver=None):
        if driver is None:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
        else:
            self.driver = driver
        self.__lock: Lock = Lock()

    def enter(self, url: str):
        """
        Loads a web page in the current browser session.
        """
        try:
            self.driver.get(url)
        except:
            self.driver = webdriver.Chrome(ChromeDriverManager().install())
            self.driver.get(url)

    def __move_mouse(self):
        action = webdriver.ActionChains(self.driver)
        body = self.get_element(by=By.CSS_SELECTOR, selector="body")
        action.move_to_element(body)
        action.move_by_offset(100, 100)
        action.send_keys(Keys.TAB)
        action.send_keys(Keys.TAB)
        action.perform()

    def exists(
            self,
            by: By = By.CSS_SELECTOR,
            selector: str = "",
            wait: float = 0,
            parent=None,
            move_mouse: bool = False
    ) -> bool:
        """
        Check if an element is on the DOM
        :param parent: parent element from which to start the search
        :param by: selection way
        :param selector:
        :param wait: time spent searching for the item
        :param move_mouse:
        :return: if the element is on the DOM
        """
        if parent is None: parent = self.driver
        try:
            if move_mouse: self.__move_mouse()
            WebDriverWait(parent, wait).until(
                EC.presence_of_element_located((by, selector))
            )
        except TimeoutException:
            return False
        except Exception:
            traceback.print_exc()
            return False
        return True

    def visible(
            self,
            by: By = By.CSS_SELECTOR,
            selector: str = "",
            wait: float = 0,
            parent=None,
            move_mouse: bool = False
    ) -> bool:
        """
        Check if an element is on the DOM and is visible
        :param move_mouse:
        :param parent: parent element from which to start the search
        :param by: selection way
        :param selector:
        :param wait: time spent searching for the item
        :return: if the element is on the DOM and is visible
        """
        if parent is None: parent = self.driver
        try:
            if move_mouse: self.__move_mouse()
            WebDriverWait(parent, wait).until(
                EC.visibility_of_all_elements_located((by, selector))
            )
        except TimeoutException:
            return False
        except Exception:
            traceback.print_exc()
            return False
        return True

    def is_displayed(self, by: By = By.CSS_SELECTOR, selector: str = "") -> bool:
        # TODO
        pass

    def click(self, by: By = By.CSS_SELECTOR, selector: str = "", wait: float = 0, parent=None,
              move_mouse: bool = False) -> bool:
        """
        Try to click an element from DOM
        :param move_mouse:
        :param parent:
        :param wait:
        :param by: selection way
        :param selector:
        :return: if the element was found
        """
        try:
            if move_mouse: self.__move_mouse()
            self.get_element(by=by, selector=selector, wait=wait, parent=parent).click()
        except (NoSuchElementException, AttributeError, ElementClickInterceptedException):
            return False
        return True

    def write_input(self, by: By = By.CSS_SELECTOR, selector: str = "", text: str = "", submit: bool = False) -> bool:
        """
        Try to write a text in an input
        :param by: selection way
        :param selector:
        :param text: text to be written
        :param submit: if true submit the form
        :return: if the element was found
        """
        try:
            e = self.driver.find_element(by, selector)
            e.clear()
            e.send_keys(text)
            if submit: e.submit()
        except NoSuchElementException:
            return False
        return True

    def get_elements(self, by: By = By.CSS_SELECTOR, selector: str = "", wait: float = 0, parent=None):
        """
        Try to write a text in an input
        :param by: selection way (default xPath)
        :param selector:
        :param wait: time spent searching for the item
        :param parent: parent element from which to start the search
        :return: the content found inside the selector
        """

        if parent is None: parent = self.driver
        try:
            content = WebDriverWait(parent, wait).until(
                EC.presence_of_all_elements_located((by, selector))
            )
        except (NoSuchElementException, TimeoutException):
            return []
        return content

    def get_element(self, by: By = By.CSS_SELECTOR, selector: str = "", wait: float = 0, parent=None):
        """
        Try to write a text in an input
        :param by: selection way (default xPath)
        :param selector:
        :param wait: time spent searching for the item
        :param parent: parent element from which to start the search
        :return: the content found inside the selector
        """

        if parent is None: parent = self.driver
        try:
            content = WebDriverWait(parent, wait).until(
                EC.presence_of_all_elements_located((by, selector))
            )
        except (NoSuchElementException, TimeoutException):
            return None
        return content[0]

    def screenshot_elements(self, by: By = By.CSS_SELECTOR, selector: str = "", wait: float = 0, parent=None) -> list:
        """
        Get screenshots of visible elements from DOM
        :param by: selection way
        :param selector:
        :param wait: time spent searching for the item
        :param parent: parent element from which to start the search
        :return: a list of  RGB images (numpy array)
        """
        imgs = []
        finded_elements = self.get_elements(by=by, selector=selector, wait=wait, parent=parent)
        if len(finded_elements) == 0:
            return imgs

        for finded_element in finded_elements:
            imgs.append(self.screenshot(finded_element))
        return imgs

    def screenshot_element(self, by: By = By.CSS_SELECTOR, selector: str = "", wait: float = 0, parent=None):
        """
        Get screenshots of a visible element from DOM
        :param by: selection way
        :param selector:
        :param wait: time spent searching for the item
        :param parent: parent element from which to start the search
        :return: a RGB image (numpy array)
        """
        finded_element = self.get_element(by=by, selector=selector, wait=wait, parent=parent)

        if finded_element is None:
            print(f"SELECTOR FAIL: {selector}")
            return None

        return self.screenshot(finded_element)

    @staticmethod
    def screenshot(element=None):
        """
        Get screenshots of visible elements from DOM

        :param element: Selenium WebElement
        :return:
        """
        try:
            img = Image.open(BytesIO(element.screenshot_as_png)).convert('RGB')
            img = np.array(img)
            return img
        except WebDriverException:
            return None

    def lock(self):
        """
        Block the singleton to prevent it from being called from other threads
        """
        self.__lock.acquire()

    def unlock(self):
        """
        Unlock the singleton.
        """
        try:
            self.__lock.release()
        except RuntimeError:
            pass

    def exit(self):
        """
        Ends the current browser session
        """
        self.driver.quit()
