# Selenium
from selenium.webdriver.common.by import By
from selenium_wrapper import SeleniumWrapper

# System libraries
import uuid
import json
import webbrowser
import os
import requests
from time import sleep

# Computer vision libraries
import cv2
from fer import FER
from PIL import Image
from io import BytesIO

# Local data
from xpaths import xpaths
from credencials import EMAIL, PASS


detector = FER(mtcnn=True)


def save_data(data):
    """
    Save the data for the webpage
    :param data: data extracted from user profile posts
    :return:
    """
    json_data = json.dumps(data, indent=4)
    f = open("web/data.js", "w")
    f.write(f"let data = {json_data}")
    f.close()


def open_web():
    """
    Open the web page with collected data.
    :return:
    """
    webbrowser.open('file://' + os.path.realpath("./web/index.html"))


def scan_img(img_path):
    """
    Scan image to find faces and recognize his emotions
    :param img_path:
    :return: a copy of the image that remark the detected faces and his emotions
    """
    img = cv2.imread(img_path)

    faces = detector.detect_emotions(img)
    for face in faces:
        c = face["box"]
        v = face["emotions"]
        e = max(v.keys(), key=(lambda i: v[i]))

        cv2.rectangle(img, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), (0, 0, 0), 9)
        cv2.rectangle(img, (c[0], c[1]), (c[0] + c[2], c[1] + c[3]), (255, 255, 255), 3)
        cv2.putText(img, e, (c[0] + 3, c[1] + c[3] + 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 6)
        cv2.putText(img, e, (c[0] + 3, c[1] + c[3] + 10), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)

    return img


def scan_posts():
    """
    Scan all instagram posts
    :return:
    """
    posts = [scan_post()]

    if selenium.exists(by=By.XPATH, selector=xpaths["carrousel_next_post_button"]):
        element = selenium.get_element(by=By.XPATH, selector=xpaths["carrousel_next_post_button"])
        css_selector = f'{element.get_attribute("class").replace(" ", ".")} button'

        while selenium.exists(selector=css_selector):
            selenium.click(selector=css_selector)
            posts.append(scan_post())

    return posts


def scan_post():
    """
    Scan a instagram post
    :return:
    """
    post = {
        "photos": [],
        "comments": []
    }

    urls = scan_photo_urls()

    if selenium.exists(by=By.XPATH, selector=xpaths["carrousel_next_photo_button"]):
        element = selenium.get_element(by=By.XPATH, selector=xpaths["carrousel_next_photo_button"])
        css_selector = f'.{element.get_attribute("class").strip()}'

        while selenium.exists(selector=css_selector):
            selenium.click(selector=css_selector)
            urls += scan_photo_urls()

    aux = []
    for url in urls:
        if url not in aux:
            aux.append(url)
    urls = aux

    post["photos"] = scan_photo(urls)
    post["comments"] = scan_comments()

    return post


def scan_photo_urls():
    """
    Get the URL from post image
    :return:
    """
    urls = []
    photo_container = selenium.get_element(by=By.XPATH, selector=xpaths["carrousel_displayed_photo"], wait=10)
    photo_imgs = selenium.get_elements(selector="img", parent=photo_container)

    for photo_img in photo_imgs:
        urls.append(photo_img.get_attribute("src"))

    return urls


def scan_photo(urls):
    """
    Save images from a list URLs.
    :param urls: list of image URLS
    :return: image paths
    """

    filenames = []

    for url in urls:
        photo_filename = f"photos/{uuid.uuid4()}.jpg"
        photo_response = requests.get(url)

        photo = Image.open(BytesIO(photo_response.content))
        photo.save(photo_filename)
        filenames.append(photo_filename)

    return filenames


def scan_comments():
    """
    Scan the comment section from an instagram post
    :return:
    """

    comments = []

    if selenium.exists(by=By.XPATH, selector=xpaths["comments_box"], wait=2):
        comments_box = selenium.get_element(by=By.XPATH, selector=xpaths["comments_box"])
        comments_names_elements = selenium.get_elements(by=By.XPATH, selector=xpaths["comments_name"])
        comments_texts_elements = selenium.get_elements(by=By.XPATH, selector=xpaths["comments_text"])

        for user, text in zip(comments_names_elements, comments_texts_elements):
            comments.append({
                "user": user.get_attribute("innerHTML"),
                "text": text.get_attribute("innerHTML"),
            })

    return comments


if __name__ == '__main__':
    url = "https://www.instagram.com/"
    email = EMAIL
    password = PASS

    selenium = SeleniumWrapper()
    selenium.enter(url=url)

    # Cookies dialog
    selenium.click(by=By.XPATH, selector=xpaths["cookies_dialog_button"])

    # Username / Password
    sleep(1)
    selenium.write_input(by=By.XPATH, selector=xpaths["login_username_input"], text=EMAIL)
    selenium.write_input(by=By.XPATH, selector=xpaths["login_password_input"], text=password)
    sleep(1)

    # Login
    selenium.click(by=By.XPATH, selector=xpaths["login_button"])

    # Don't save login
    selenium.click(by=By.XPATH, selector=xpaths["decline_save_login_button"], wait=10)

    # Don`t activate notifications
    selenium.click(by=By.XPATH, selector=xpaths["decline_notifications_button"], wait=10)

    # Go to profile
    selenium.click(by=By.XPATH, selector=xpaths["user_button"], wait=10)
    selenium.click(by=By.XPATH, selector=xpaths["profile_button"], wait=10)

    # Open first photo
    selenium.click(by=By.XPATH,
                   selector=xpaths["first_profile_photo"],
                   wait=10)

    # Scan posts
    data = scan_posts()

    # Close web bot
    selenium.exit()

    # Scan images
    for post in data:
        for photo in post["photos"]:
            img = scan_img(photo)
            cv2.imwrite(photo, img)

    # Save data
    save_data(data)

    # Open web
    open_web()
