# coding: utf-8
import base64
import time
from ctypes import windll

import numpy as np
import cv2
import pyautogui
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from utils.OracleConn import OracleConnection
from utils.configRead import ReadConfig
from utils.log import HandleLog
import random


class JDLogin:

    def __init__(self):
        self.logs = HandleLog("京麦登录")
        self.__creat_browser()

    def __creat_browser(self):
        try:
            # options = webdriver.()
            # if not settings.LOAD_IMAGES:
            #     prefs = {"profile.managed_default_content_settings.images": "2"}
            #     options.add_experimental_option("prefs", prefs)
            # options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            driver = webdriver.Ie()
            # driver.set_page_load_timeout(30)
            # driver.set_script_timeout(30)
            self.driver = driver
            self.wait = WebDriverWait(self.driver, 60)
            self.logs.info("【浏览器初始化成功】")
        except Exception as e:
            self.logs.error(f"【浏览器初始化失败, {e}】")
            return

    def visit_login_page(self):
        login_url = "https://passport.shop.jd.com/login/index.action"
        self.driver.get(login_url)
        time.sleep(5)

    def bs64toimg(self, bs64code, img_name):

        imgdata = base64.b64decode(bs64code.replace("data:image/png;base64,", ""))
        with open(f'./{img_name}', 'wb') as file:
            file.write(imgdata)

    def download_captcha_image(self, cssStr, img_name):
        img_ = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, cssStr)))
        code_img = img_.get_attribute("src")
        print("download_captcha_image", code_img)
        self.bs64toimg(code_img, img_name)

    def get_distance(self):
        img = cv2.imread('image.png', 0)
        template = cv2.imread('template.png', 0)
        res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED)
        value = cv2.minMaxLoc(res)[2][0]
        distance = value * 278 / 360
        return distance

    def ease_out_quart(self, x):
        return 1 - pow(1 - x, 4)

    def get_tracks_2(self, distance, seconds, ease_func):
        """
        根据轨迹离散分布生成的数学 生成  # 参考文档  https://www.jianshu.com/p/3f968958af5a
        成功率很高 90% 往上
        :param distance: 缺口位置
        :param seconds:  时间
        :param ease_func: 生成函数
        :return: 轨迹数组
        """
        distance *= 359 / 360
        tracks = [0]
        offsets = [0]
        for t in np.arange(0.0, seconds, 0.1):
            ease = ease_func
            offset = round(ease(t / seconds) * distance)
            tracks.append(offset - offsets[-1])
            offsets.append(offset)
        return tracks

    def move_to_gap(self, slider, distance, tracks):
        ActionChains(self.driver).click_and_hold(slider).perform()
        for index, x in enumerate(tracks):
            y = random.uniform(0, 1.5)
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=y).perform()
        ActionChains(self.driver).release().perform()
        print("拖动完成")

    def imouse_drag(self, x1=1216, y1=527, x2=None, y2=530, button='left', speed=10):
        # (x1,y1)，(x2,y2)分别表示：鼠标移动的初末坐标点
        try:
            # dll = windll.LoadLibrary(r"C:\Program Files\IS-RPA10\Plugin\Com.Isearch.Func.AutoIt\AutoItX3.dll")
            dll = windll.LoadLibrary(r"E:\AutoIt3\AutoItX\AutoItX3_x64.dll")
            # 对象为：本地的一个动态链接库文件
            return dll.AU3_MouseClickDrag(button, x1, y1, x2, y2, speed)
        # 使用鼠标点击拖动方法
        except Exception as e:
            raise e

    def login(self, username, password):
        self.visit_login_page()
        account_login = self.wait.until(EC.presence_of_element_located((By.ID, "account-login")))
        js = 'arguments[0].click()'
        self.driver.execute_script(js, account_login)
        time.sleep(2)
        # 进入iframe
        iframe = self.wait.until(EC.presence_of_element_located((By.ID, "loginFrame")))
        self.driver.switch_to_frame(iframe)
        # time.sleep(2)
        # login_name = self.wait.until(EC.presence_of_element_located((By.ID, "loginname")))
        # login_name.clear()
        # login_name.send_keys(username)

        login_pwd = self.wait.until(EC.presence_of_element_located((By.ID, "nloginpwd")))
        login_pwd.clear()
        login_pwd.send_keys(password)

        login_btn = self.wait.until(EC.presence_of_element_located((By.ID, "paipaiLoginSubmit")))
        self.driver.execute_script(js, login_btn)
        time.sleep(5)
        bigimg_css = "div.JDJRV-bigimg > img"
        self.download_captcha_image(bigimg_css, "image.png")
        smallimg_css = "div.JDJRV-smallimg > img"
        self.download_captcha_image(smallimg_css, "template.png")

        time.sleep(2)
        slide_btn = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.JDJRV-slide-btn')))
        print(55555, slide_btn)
        distance = self.get_distance()
        print(distance)
        # tracks = self.get_tracks_2(distance, seconds=2, ease_func=self.ease_out_quart)
        # print(tracks)
        # self.move_to_gap(slide_btn, distance, tracks)
        self.imouse_drag(x2=distance+1216)

    # def __del__(self):
    #     self.driver.close()


if __name__ == '__main__':
    app = JDLogin()
    username = "京联专卖店-海尔"
    # password = "hq123456a"
    password = "a"
    app.login(username, password)
