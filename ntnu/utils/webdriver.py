''' Libraries '''
import io
import os
import json
import time
import logging
from unittest import result
my_selenium_logger = logging.getLogger(name="selenium-wire")
# import winsound
# import requests
# import datetime
from PIL import Image
from seleniumwire import webdriver

from mapping import domain_code2text
from exceptions import *
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


def wait_to_click(element):
    for _ in range(15):
        try:
            element.click()
            time.sleep(1)
            return
        except:
            time.sleep(0.2)
    raise SeleniumStuckException


# def wait_for_url(driver, url_content):
#     for _ in range(20):
#         time.sleep(0.25)
#         if url_content in driver.current_url: return
#     raise SeleniumStuckException


def wait_and_find_element_by_id(driver, id):
    for _ in range(25):
        try:
            element = driver.find_element_by_id(id)
            return element
        except:
            time.sleep(0.2)
    raise SeleniumStuckException


def wait_and_find_element_by_name(driver, name):
    for _ in range(25):
        try:
            element = driver.find_element_by_name(name)
            return element
        except:
            time.sleep(0.2)
    raise SeleniumStuckException


def wait_and_find_elements_by_name(driver, name):
    for _ in range(25):
        try:
            elements = driver.find_elements_by_name(name)
            return elements
        except:
            time.sleep(0.2)
    raise SeleniumStuckException


def wait_and_find_element_by_class(driver, class_):
    for _ in range(50):
        try:
            element = driver.find_element_by_class(class_)
            return element
        except:
            time.sleep(0.2)
    raise SeleniumStuckException


def wait_domain_option_by_text(driver, text):
    for _ in range(50):
        try:
            element = driver.find_element_by_xpath(f"//li[@role='option'][contains(text(), {text})]")
            return element
        except:
            time.sleep(0.2)
    raise SeleniumStuckException
    

def wait_for_random_id_button(driver):
    for _ in range(50):
        try:
            element = driver.find_element_by_xpath(f"//span[contains(text(), '確認')]")
            element = element.find_element_by_xpath("..")
            return element
        except:
            time.sleep(0.2)
    raise SeleniumStuckException


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
            message = driver.find_element_by_id("messagebox-1001-displayfield-inputEl").text
            if "請稍候" in message: raise Exception
        except:
            time.sleep(0.2)
    if "學號" in message:
        raise StudentIdNotExistException
    elif "密碼" in message:
        raise PasswordWrongException
    elif "驗證碼" in message:
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
    raise SeleniumStuckException


def wait_for_validate_code_button(driver, button):
    for _ in range(25):
        buttons = driver.find_elements_by_class_name("x-btn-button")
        if len(buttons) == 19:
            if button == "confirm": return buttons[17]
            else                  : return buttons[18]
        time.sleep(0.2)
    raise SeleniumStuckException


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


def login_course_taking_system(student_id, password, take_course=False,
                               course_no=None, domain=None):

    if take_course:
        assert course_no is not None
        assert domain    is not None
        if domain != '': domain = domain_code2text[domain]

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(WEBDRIVER_PATH, options=options)
    driver.get(NTNU_LOGIN_CHECK_URL)

    # 驗證碼: 正確 或 錯誤
    for try_turn in range(5):
        
        # 驗證碼破圖
        validate_code_img_broken_time = 0
        while True:
            validate_code_img = wait_for_validate_code_img(driver)
            if validate_code_img is not None: break
            else:
                wait_to_click(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"))  # 「重新產生」按鈕
                retry_time = validate_code_img_broken_time * 2 + 3
                time.sleep(retry_time)
                validate_code_img_broken_time += 1

        validate_code = dl_model.predict(validate_code_img)
        validate_code = process_validate_code(validate_code)
        wait_and_find_element_by_id(driver, "validateCode-inputEl").send_keys(validate_code)

        wait_and_find_element_by_id(driver, "userid-inputEl").clear()
        wait_and_find_element_by_id(driver, "userid-inputEl").send_keys(student_id)
        wait_and_find_element_by_id(driver, "password-inputEl").send_keys(password)
        wait_to_click(wait_and_find_element_by_id(driver, "button-1016-btnEl"))  # 「登入」按鈕

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

        wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnEl"))  # 「OK」按鈕
        time.sleep(3)
        wait_to_click(wait_and_find_element_by_id(driver, "redoValidateCodeButton-btnEl"))  # 「重新產生」按鈕


    try:
        wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnEl"))  # 教程學生的「OK」按鈕
    except:
        pass
    wait_to_click(wait_and_find_element_by_id(driver, "button-1017-btnEl"))  # 「下一頁」按鈕
    name  = wait_and_find_element_by_id(driver, "panel-1011-innerCt").find_elements("tag name", "font")[1].text
    major = wait_and_find_element_by_id(driver, "panel-1012-innerCt").find_elements("tag name", "font")[1].text.split(' ')[0]
    wait_and_find_element_by_id(driver, "now")
    driver.execute_script("document.getElementById('now').parentElement.remove()")  # 移除計時器
    driver.switch_to.frame(wait_and_find_element_by_id(driver, "stfseldListDo"))

    if not take_course:
        cookies = driver.get_cookies()[0]
        driver.quit()
        return cookies, name, major
    
    else:
        wait_to_click(wait_and_find_element_by_id(driver, "add-btnEl"))  # 「加選」按鈕
        wait_and_find_element_by_id(driver, "serialNo-inputEl").send_keys(course_no)

        # 驗證碼: 正確 或 錯誤
        time.sleep(0.2)
        for try_turn in range(5):

            # 驗證碼破圖
            validate_code_img_broken_time = 0
            while True:
                wait_to_click(wait_and_find_element_by_id(driver, "button-1060-btnEl"))  # 「開課序號直接加選儲存」按鈕

                # 如果是通識課：選領域
                if domain in [ "語言與文學", "藝術與美感", "哲學思維與道德推理", "公民素養與社會探究",
                            "歷史與文化", "數學與邏輯思維", "科學與生命", ]:
                    wait_to_click(wait_and_find_element_by_id(driver, "domainType-inputEl"))  # 「選擇通識領域」下拉 bar 按鈕
                    wait_to_click(wait_domain_option_by_text(driver, domain))                 # 各領域選項
                    wait_to_click(wait_for_random_id_button(driver))                          # 「確認」按鈕

                wait_for_validate_code_img(driver)
                validate_code_img = wait_for_validate_code_img(driver)
                if validate_code_img is not None: break
                else:
                    wait_to_click(wait_for_validate_code_button(driver, "cancel"))  # 「取消」按鈕
                    wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                    retry_time = validate_code_img_broken_time * 2 + 3
                    time.sleep(retry_time)
                    validate_code_img_broken_time += 1
            
            validate_code = dl_model.predict(validate_code_img)
            validate_code = process_validate_code(validate_code)
            wait_and_find_element_by_id(driver, "valid-inputEl").send_keys(validate_code)
            wait_to_click(wait_for_validate_code_button(driver, "confirm"))  # 「確認」按鈕

            # result = wait_element_text_by_id(driver, "messagebox-1001-displayfield-inputEl", ["驗證碼錯誤", "額滿", "衝堂", "重複登記", "儲存成功"])
            result = wait_element_text_by_id(driver, "messagebox-1001-displayfield-inputEl")

            if result == "驗證碼錯誤":
                wait_to_click(wait_and_find_element_by_id(driver, "button-1005-btnIconEl"))  # 「OK」按鈕
                if try_turn == 4:
                    result = "驗證碼連續 5 次錯誤"
                    break
                time.sleep(3)
            else:
                break

        driver.quit()
        return result


def login_iportal(student_id, password):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(WEBDRIVER_PATH, options=options)
    driver.get(NTNU_IPORTAL_URL)
    wait_and_find_element_by_id(driver, "muid").send_keys(student_id)
    wait_and_find_element_by_id(driver, "mpassword").send_keys(password)
    wait_to_click(wait_and_find_element_by_name(driver, "Submit22"))  # 「登入」按鈕
    wait_to_click(wait_and_find_elements_by_name(driver, "apFolder")[1])  # 「教務相關系統」列表
    wait_to_click(wait_and_find_element_by_id(driver, "ap-acadm").find_elements("tag name", "li")[5])  # 「教務相關系統」列表
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    wait_to_click(wait_and_find_element_by_id(driver, "treeview-1013-record-37"))  # 「成績查詢」列表
    history = json.loads(wait_for_course_history(driver))
    driver.quit()
    return history