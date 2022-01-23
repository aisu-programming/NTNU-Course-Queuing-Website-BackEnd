''' Libraries '''
import io
import json
import os
import time
# import winsound
# import requests
# import datetime
from PIL import Image
from seleniumwire import webdriver

from exceptions import *
from validation.model import model


''' Settings '''
# from app import dl_model
dl_model = model
# dl_model = None




''' Parameters '''
PATH            = os.path.abspath(__file__)
DIR_PATH        = os.path.dirname(PATH)
WEBDRIVER_PATH  = os.path.join(os.path.dirname(DIR_PATH), "chromedriver_win32/chromedriver.exe")
RESIZE_HEIGHT   = int(os.environ.get("RESIZE_HEIGHT"))
RESIZE_WIDTH    = int(os.environ.get("RESIZE_WIDTH"))

NTNU_WEBSITE_NO       = os.environ.get("NTNU_WEBSITE_NO")
NTNU_WEBSITE_PREFIX   = f"https://cos{NTNU_WEBSITE_NO}s.ntnu.edu.tw/AasEnrollStudent"
NTNU_LOGIN_CHECK_URL  = f"{NTNU_WEBSITE_PREFIX}/LoginCheckCtrl?language=TW"
NTNU_COURSE_QUERY_URL = f"{NTNU_WEBSITE_PREFIX}/CourseQueryCtrl"
NTNU_ENROLL_URL       = f"{NTNU_WEBSITE_PREFIX}/EnrollCtrl"
NTNU_IPORTAL_URL      = "https://iportal.ntnu.edu.tw/ntnu/"



''' Functions '''
# def beep_sound():
#     for _ in range(5):
#         winsound.Beep(800, 800)
#         time.sleep(0.2)
#     return


# def send_LineNotification(access_token, message):
#     headers = {
#         "Authorization": f"Bearer {access_token}",
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     params = {"message": message}
#     requests.post(
#         "https://notify-api.line.me/api/notify",
#         headers=headers, params=params
#     )
#     return


# def my_time_str(start_time=None):
#     if start_time is not None:
#         interval = time.time() - start_time
#         return f"{datetime.datetime.now().strftime(f'%H:%M:%S')} | {int(interval//60):>2}min {int(interval%60):>2}sec"
#     else:
#         return f"{datetime.datetime.now().strftime(f'%H:%M:%S')}"


# def wait_until_9_am():
#     while True:
#         hour = int(datetime.datetime.now().strftime(f'%H'))
#         if hour >= 9: break
#         os.system("cls")
#         print(f"{my_time_str()} | Waiting until 9 AM...\n")
#         time.sleep(1)


def click_and_wait(element):
    for _ in range(25):
        try:
            element.click()
            time.sleep(1)
            return
        except:
            time.sleep(0.2)
    raise BrowserStuckException


# def wait_for_url(driver, url_content):
#     for _ in range(20):
#         time.sleep(0.25)
#         if url_content in driver.current_url: return
#     raise BrowserStuckError


def wait_and_find_element_by_id(driver, id):
    for _ in range(25):
        try:
            element = driver.find_element_by_id(id)
            return element
        except:
            time.sleep(0.2)
    raise BrowserStuckException


def wait_and_find_element_by_name(driver, name):
    for _ in range(25):
        try:
            element = driver.find_element_by_name(name)
            return element
        except:
            time.sleep(0.2)
    raise BrowserStuckException


def wait_and_find_elements_by_name(driver, name):
    for _ in range(25):
        try:
            elements = driver.find_elements_by_name(name)
            return elements
        except:
            time.sleep(0.2)
    raise BrowserStuckException


def wait_and_find_element_by_class(driver, class_):
    for _ in range(50):
        try:
            element = driver.find_element_by_class(class_)
            return element
        except:
            time.sleep(0.2)
    raise BrowserStuckException
    

def wait_for_button_appear(driver):
    message = ''
    for _ in range(50):
        try:
            driver.find_element_by_id("button-1017-btnEl")  # 「下一頁」按鈕
            return True
        except:
            pass
        try:
            driver.find_element_by_id("button-1005-btnEl")  # 「OK」按鈕
            message = driver.find_element_by_id("messagebox-1001-displayfield-inputEl").text()
            break
        except:
            time.sleep(0.2)
    if message == "驗證碼錯誤": return False
    else                     : raise PasswordWrongException


# def wait_element_text_by_id(driver, id, texts):
#     for _ in range(25):
#         try:
#             element = driver.find_element_by_id(id)
#             for i, text in enumerate(texts):
#                 if text in element.text: return i  # return condition id
#             raise CourseTakenException
#         except:
#             time.sleep(0.2)
#     raise BrowserStuckError


# def wait_for_validate_code_button(driver, button):
#     for _ in range(25):
#         buttons = driver.find_elements_by_class_name("x-btn-button")
#         if len(buttons) == 19:
#             if button == "confirm": return buttons[17]
#             else                  : return buttons[18]
#         time.sleep(0.2)
#     raise BrowserStuckError


def wait_for_validate_code_img(driver):
    for _ in range(5):
        for request in reversed(driver.requests):
            if "RandImage" in request.url:
                if request.response == None:
                    return None
                else:
                    img = Image.open(io.BytesIO(request.response.body)).convert('L').resize((RESIZE_WIDTH, RESIZE_HEIGHT))
                    return img
        time.sleep(0.2)
    return None


def wait_for_course_history(driver):
    for _ in range(5):
        for request in reversed(driver.requests):
            if "AccseldServlet.do?action=scorelist" in request.url:
                return request.response.body
        time.sleep(0.2)
    return None


number_map = { str(i): i for i in range(10) }
def process_validate_code(validate_code):
    if '=' in validate_code:
        number_1 = number_map[validate_code[0]]
        number_2 = number_map[validate_code[2]]
        if   validate_code[1] == '+': return number_1 + number_2
        elif validate_code[1] == '-': return number_1 - number_2
        elif validate_code[1] == '*': return number_1 * number_2
    else:
        return ''.join(validate_code)


def login_course_taking_system(student_id, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(WEBDRIVER_PATH, options=options)
    driver.get(NTNU_LOGIN_CHECK_URL)

    # 驗證碼: 正確 或 錯誤
    while True:
        
        # 驗證碼破圖
        validate_code_img_broken_time = 0
        while True:
            validate_code_img = wait_for_validate_code_img(driver)
            if validate_code_img is not None: break
            else:
                click_and_wait(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"))  # 「重新產生」按鈕
                retry_time = validate_code_img_broken_time * 2 + 3
                time.sleep(retry_time)
                validate_code_img_broken_time += 1

        validate_code = dl_model.predict(validate_code_img)
        validate_code = process_validate_code(validate_code)
        wait_and_find_element_by_id(driver, "validateCode-inputEl").send_keys(validate_code)

        wait_and_find_element_by_id(driver, "userid-inputEl").clear()
        wait_and_find_element_by_id(driver, "userid-inputEl").send_keys(student_id)
        wait_and_find_element_by_id(driver, "password-inputEl").send_keys(password)
        click_and_wait(wait_and_find_element_by_id(driver, "button-1016-btnEl"))  # 「登入」按鈕

        try:
            if wait_for_button_appear(driver): break
        except PasswordWrongException:
            driver.quit()
            raise PasswordWrongException

        click_and_wait(wait_and_find_element_by_id(driver, "button-1005-btnEl"))  # 「OK」按鈕
        time.sleep(3)
        click_and_wait(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"))  # 「重新產生」按鈕

    click_and_wait(wait_and_find_element_by_id(driver, "button-1017-btnEl"))  # 「下一頁」按鈕
    name  = wait_and_find_element_by_id(driver, "panel-1011-innerCt").find_elements("tag name", "font")[1].text
    major = wait_and_find_element_by_id(driver, "panel-1012-innerCt").find_elements("tag name", "font")[1].text.split(' ')[0]
    wait_and_find_element_by_id(driver, "now")
    driver.execute_script("document.getElementById('now').parentElement.remove()")  # 移除計時器
    driver.switch_to.frame(wait_and_find_element_by_id(driver, "stfseldListDo"))
    # click_and_wait(wait_and_find_element_by_id(driver, "add-btnEl"))  # 「加選」按鈕
    cookie = driver.get_cookies()[0]
    driver.quit()
    return cookie, name, major


def login_iportal(student_id, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(WEBDRIVER_PATH, options=options)
    driver.get(NTNU_IPORTAL_URL)
    wait_and_find_element_by_id(driver, "muid").send_keys(student_id)
    wait_and_find_element_by_id(driver, "mpassword").send_keys(password)
    click_and_wait(wait_and_find_element_by_name(driver, "Submit22"))  # 「登入」按鈕
    click_and_wait(wait_and_find_elements_by_name(driver, "apFolder")[1])  # 「教務相關系統」列表
    click_and_wait(wait_and_find_element_by_id(driver, "ap-acadm").find_elements("tag name", "li")[5])  # 「教務相關系統」列表
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    click_and_wait(wait_and_find_element_by_id(driver, "treeview-1013-record-37"))  # 「成績查詢」列表
    history = json.loads(wait_for_course_history(driver))
    driver.quit()
    return history