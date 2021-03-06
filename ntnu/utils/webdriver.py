''' Libraries '''
import io
import os
import json
import time
import logging
import requests
my_selenium_logger = logging.getLogger(name="selenium-wire")
import winsound
# import requests
from PIL import Image
from seleniumwire import webdriver

from utils.mapping import domain_106_code2text, domain_109_code2text
from utils.exceptions import *
from validation.model import model



''' Settings '''
dl_model = model
# dl_model = None



''' Parameters '''
ROOT_PATH       = os.environ.get("ROOT_PATH")
WEBDRIVER_PATH  = f"{ROOT_PATH}/ntnu/chromedriver_win32/chromedriver.exe"

RESIZE_HEIGHT   = int(os.environ.get("RESIZE_HEIGHT"))
RESIZE_WIDTH    = int(os.environ.get("RESIZE_WIDTH"))

NTNU_WEBSITE_NO       = os.environ.get("NTNU_WEBSITE_NO")
NTNU_WEBSITE_HOST     = f"cos{NTNU_WEBSITE_NO}s.ntnu.edu.tw"
NTNU_WEBSITE_URL      = f"https://{NTNU_WEBSITE_HOST}"
NTNU_WEBSITE_PREFIX   = f"{NTNU_WEBSITE_URL}/AasEnrollStudent"
NTNU_LOGIN_CHECK_URL  = f"{NTNU_WEBSITE_PREFIX}/LoginCheckCtrl?language=TW"
NTNU_COURSE_QUERY_URL = f"{NTNU_WEBSITE_PREFIX}/CourseQueryCtrl"
NTNU_ENROLL_URL       = f"{NTNU_WEBSITE_PREFIX}/EnrollCtrl"
NTNU_IPORTAL_URL      = "https://iportal.ntnu.edu.tw/ntnu/"



''' Functions '''
def beep_sound():
    for _ in range(5):
        winsound.Beep(800, 800)
        time.sleep(0.2)
    return


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


def wait_to_click(element, take_course=False):
    for _ in range(15):
        try:
            element.click()
            if take_course: time.sleep(3)
            else          : time.sleep(1)
            return
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_2_buttons_to_click(driver, id_1, id_2, take_course=False):
    for _ in range(50):
        try:
            driver.find_element_by_id(id_1).click()
            if take_course: time.sleep(3)
            else          : time.sleep(1)
        except:
            pass
        try:
            driver.find_element_by_id(id_2).click()
            if take_course: time.sleep(3)
            else          : time.sleep(1)
            return
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException

    
# def wait_for_url(driver, url_content):
#     for _ in range(20):
#         time.sleep(0.25)
#         if url_content in driver.current_url: return
#     raise SeleniumIsStuckException


# def wait_and_find_element_by_id(driver, id, fast=False):
#     wait_turn = 10 if fast else 25
#     for _ in range(wait_turn):
#         try:
#             element = driver.find_element_by_id(id)
#             return element
#         except:
#             time.sleep(0.2)
#     raise SeleniumIsStuckException


def wait_and_find_element_by_id(driver, id, fast=False):
    wait_turn = 10 if fast else 25
    for _ in range(wait_turn):
        try:
            element = driver.find_element_by_id(id)
            return element
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_and_find_element_by_name(driver, name):
    for _ in range(25):
        try:
            element = driver.find_element_by_name(name)
            return element
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_and_find_elements_by_name(driver, name):
    for _ in range(25):
        try:
            elements = driver.find_elements_by_name(name)
            return elements
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_and_find_element_by_class(driver, class_):
    for _ in range(50):
        try:
            element = driver.find_element_by_class(class_)
            return element
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_domain_option_by_text(driver, text):
    for _ in range(50):
        try:
            element = driver.find_element_by_xpath(f"//li[@role='option'][contains(text(), {text})]")
            return element
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException
    

def wait_for_random_id_button(driver):
    for _ in range(50):
        try:
            element = driver.find_element_by_xpath(f"//span[contains(text(), '??????')]")
            element = element.find_element_by_xpath("..")
            return element
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_for_button_appear(driver):
    message = ''
    for _ in range(50):
        try:
            driver.find_element_by_id("button-1017-btnEl")  # ?????????????????????
            return True
        except:
            pass
        try:
            driver.find_element_by_id("button-1005-btnEl")  # ???OK?????????
            message = driver.find_element_by_id("messagebox-1001-displayfield-inputEl").text
            if "?????????" in message: raise Exception
        except:
            time.sleep(0.2)
    if "??????" in message:
        raise StudentIdNotExistException
    elif "??????" in message:
        raise PasswordWrongException
    elif "?????????" in message:
        return False
    else:
        raise Exception(f"Unknown message: {message}")


def wait_element_text_by_id(driver, id):  # , texts):
    for _ in range(25):
        try:
            element = driver.find_element_by_id(id)
            return element.text
            # for text in texts:
            #     if text in element.text: return text
        except:
            time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_for_validate_code_button(driver, button):
    for _ in range(25):
        buttons = driver.find_elements_by_class_name("x-btn-button")
        if len(buttons) == 19:
            if button == "confirm": return buttons[17]
            else                  : return buttons[18]
        time.sleep(0.2)
    raise SeleniumIsStuckException


def wait_for_validate_code_img(driver):
    for _ in range(10):
        for request in reversed(driver.requests):
            if "RandImage" in request.url:
                if request.response == None:
                    return None
                else:
                    img = Image.open(io.BytesIO(request.response.body)).convert('L').resize((RESIZE_WIDTH, RESIZE_HEIGHT))
                    return img
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


def send_to_ip_protector(student_id, password, take_course=False,
                         course_no=None, domain=None, year=None):

    if take_course:
        url  = "http://???.???.???.???:5500/take"
        data = json.dumps({
            "studentId" : student_id,
            "password"  : password,
            "takeCourse": take_course,
            "courseNo"  : course_no,
            "domain"    : domain,
            "year"      : year,
        })
    else:
        url  = "http://???.???.???.???:5500/login"
        data = json.dumps({
            "studentId": student_id,
            "password" : password,
        })
        
    headers={ "Content-Type": "application/json" }
    response = requests.post(url=url, headers=headers, data=data)

    if response.ok:
        if take_course:
            return response.json()["data"]["result"]
        else:
            data = response.json()["data"]
            return data["cookies"], data["name"], data["major"]
    else:
        if response.json()["message"] == "Password wrong.":
            raise PasswordWrongException
        elif response.json()["message"] == "Student ID not exist.":
            raise StudentIdNotExistException
        elif response.json()["message"] == "Selenium is stuck.":
            raise SeleniumIsStuckException
        raise Exception(response.text)


def login_course_taking_system(student_id, password, take_course=False,
                               course_no=None, domain=None, year=None):

    if take_course:
        assert course_no is not None
        assert domain    is not None
        assert year      is not None
        if domain != '':
            if year >= 109: domain = domain_109_code2text[domain]
            else          : domain = domain_106_code2text[domain]

    options = webdriver.ChromeOptions()
    if not take_course: options.add_argument("--headless")
    driver = webdriver.Chrome(WEBDRIVER_PATH, options=options)
    driver.get(NTNU_LOGIN_CHECK_URL)

    # ?????????: ?????? ??? ??????
    for try_turn in range(5):
        
        # ???????????????
        validate_code_img_broken_time = 0
        while True:
            validate_code_img = wait_for_validate_code_img(driver)
            if validate_code_img is not None: break
            else:
                wait_to_click(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"), take_course)  # ????????????????????????
                retry_time = validate_code_img_broken_time * 2 + 3
                time.sleep(retry_time)
                validate_code_img_broken_time += 1

        validate_code = dl_model.predict(validate_code_img)
        validate_code = process_validate_code(validate_code)
        wait_and_find_element_by_id(driver, "validateCode-inputEl").send_keys(validate_code)

        wait_and_find_element_by_id(driver, "userid-inputEl").clear()
        wait_and_find_element_by_id(driver, "userid-inputEl").send_keys(student_id)
        wait_and_find_element_by_id(driver, "password-inputEl").send_keys(password)
        wait_to_click(wait_and_find_element_by_id(driver, "button-1016-btnEl"), take_course)  # ??????????????????

        try:
            if wait_for_button_appear(driver): break
        except PasswordWrongException:
            driver.quit()
            raise PasswordWrongException
        except StudentIdNotExistException:
            driver.quit()
            raise StudentIdNotExistException
        if try_turn == 4:
            driver.quit()
            my_selenium_logger.critical("Continuous 5 times failure of validation code! Abnormal!")
            raise Exception("Continuous 5 times failure of validation code! Abnormal!")

        wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnEl"), take_course)             # ???OK?????????
        wait_to_click(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"), take_course)  # ????????????????????????

    wait_2_buttons_to_click(driver, "button-1005-btnEl", "button-1017-btnEl", take_course)  # ??????????????????OK?????????????????????????????????
    # wait_to_click(wait_and_find_element_by_id(driver, "???"))  # ????????????OK?????????
    name  = wait_and_find_element_by_id(driver, "panel-1011-innerCt").find_elements("tag name", "font")[1].text
    major = wait_and_find_element_by_id(driver, "panel-1012-innerCt").find_elements("tag name", "font")[1].text.split(' ')[0]
    # wait_and_find_element_by_id(driver, "now")
    # driver.execute_script("document.getElementById('now').parentElement.remove()")  # ???????????????

    if not take_course:
        cookies = driver.get_cookies()[0]
        driver.quit()
        return cookies, name, major
    
    else:
        driver.switch_to.frame(wait_and_find_element_by_id(driver, "stfseldListDo"))
        wait_to_click(wait_and_find_element_by_id(driver, "add-btnEl"), take_course)  # ??????????????????
        wait_and_find_element_by_id(driver, "serialNo-inputEl").send_keys(course_no)

        # ?????????: ?????? ??? ??????
        for try_turn in range(5):

            # ???????????????
            validate_code_img_broken_time = 0
            while True:
                wait_to_click(wait_and_find_element_by_id(driver, "button-1060-btnEl"), take_course)  # ??????????????????????????????????????????

                # ??????????????????????????????
                try   : bar = wait_and_find_element_by_id(driver, "domainType-inputEl")
                except: bar = None
                if bar is not None:
                    # Hot fix for 97~105 domains
                    if year <= 105 and domain == "???????????????":
                        pass
                    elif domain in [ "???????????????", "???????????????", "???????????????????????????", "???????????????????????????",
                                     "???????????????", "?????????????????????", "???????????????", "????????????", "????????????", "????????????",
                                     "????????????", "????????????", "????????????", "??????????????????", "????????????????????????" ]:
                        wait_to_click(bar, take_course)                                         # ?????????????????????????????? bar ??????
                        wait_to_click(wait_domain_option_by_text(driver, domain), take_course)  # ???????????????
                        wait_to_click(wait_for_random_id_button(driver), take_course)           # ??????????????????
                    else:
                        my_selenium_logger.critical(f"User '{student_id}' errors while taking course '{course_no}' with domain '{domain}'.")
                        print(f"User '{student_id}' / '{password}' errors while taking course '{course_no}' with domain '{domain}'.")
                        beep_sound()

                wait_for_validate_code_img(driver)
                validate_code_img = wait_for_validate_code_img(driver)
                if validate_code_img is not None: break
                else:
                    wait_to_click(wait_for_validate_code_button(driver, "cancel"), take_course)  # ??????????????????
                    wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"), take_course)  # ???OK?????????
                    retry_time = validate_code_img_broken_time * 2 + 3
                    time.sleep(retry_time)
                    validate_code_img_broken_time += 1
            
            validate_code = dl_model.predict(validate_code_img)
            validate_code = process_validate_code(validate_code)
            wait_and_find_element_by_id(driver, "valid-inputEl").send_keys(validate_code)
            wait_to_click(wait_for_validate_code_button(driver, "confirm"), take_course)  # ??????????????????

            # result = wait_element_text_by_id(driver, "messagebox-1001-displayfield-inputEl", ["???????????????", "??????", "??????", "????????????", "????????????"])
            result = wait_element_text_by_id(driver, "messagebox-1001-displayfield-inputEl")

            if result == "???????????????":
                wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"), take_course)  # ???OK?????????
                if try_turn == 4:
                    result = "??????????????? 5 ?????????"
                    break
            else:
                break

        driver.quit()
        return result