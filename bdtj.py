import time
import pymysql
import datetime
from PIL import Image
from lxml import etree
from pyquery import PyQuery as pq
from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from urllib.parse import quote

from baidutongji.config import *
from baidutongji.chaojiying import Chaojiying


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 10)


class baidutongji(object):
    def __init__(self):
        self.username = USERNAME
        self.password = PASSWORD
        self.chaojiying = Chaojiying(CHAOJIYING_USERNAME, CHAOJIYING_PASSWORD, CHAOJIYING_SOFT_ID)


    def get_code(self):
        # 调用chaojiying.py发送获取到的识别验证码
        byteimg = open("E:/jobprojects/baidutongji/codeimg.png", "rb").read()
        result = self.chaojiying.post_pic(byteimg, CHAOJIYING_KIND)
        code = result.get('pic_str')
        return code


    def save_mysql(self, PV, UV):
        """
        保存PV和UV都Mysql数据库
        :param PV:
        :param UV:
        """
        today = datetime.date.today()
        oneday = datetime.timedelta(days=1)
        yesterday = today - oneday
        db = pymysql.connect(host=HOST, port=PORT, user=USER, password=SQLPASSWORD, db=DB)
        sql = "INSERT INTO pv VALUES (%s, %s, %s);"
        cuser = db.cursor()
        cuser.execute(sql, (yesterday, PV, UV))
        db.commit()
        cuser.close()
        db.close()

    def login(self):
        # 最大化窗口
        driver.maximize_window()
        # 访问页面
        driver.get('https://tongji.baidu.com/web/welcome/login')
        # 获取登陆按钮并点击
        denglu = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#login')))
        denglu.click()
        # 获取用户输入框,密码输入框，验证码输入框
        inputusr = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#uc-common-account')))
        inputpwd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#ucsl-password-edit')))
        inputcod = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#uc-common-token')))
        # 获取验证码位置
        imgelement = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#token-img')))
        time.sleep(2)
        # 获取元素位置上，下，左，右坐标
        location = imgelement.location
        size = imgelement.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size['width']
        # 获取页面截图
        screenshot = driver.get_screenshot_as_png()
        # 将图片二进制化
        screenshot = Image.open(BytesIO(screenshot))
        # 根据验证码坐标截图并保存
        captcha = screenshot.crop((left, top, right, bottom))
        captcha.save("E:/jobprojects/baidutongji/codeimg.png")
        code = self.get_code()
        # 输入用户名密码
        inputusr.send_keys(self.username)
        inputpwd.send_keys(self.password)
        inputcod.send_keys(code)
        # 登陆提交按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#submit-form')))
        submit.click()
        # 获取昨天的PV
        time.sleep(5)
        PV = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody>tr:first-child>td:nth-child(6)>div>div:nth-child(2)'))).text
        UV = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'tbody>tr:first-child>td:nth-child(7)>div>div:nth-child(2)'))).text
        self.save_mysql(PV, UV)
        # cookies = driver.get_cookies()



run = baidutongji()
run.login()