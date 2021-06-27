'''
@author: 178me
@description: 完成广财慕课学习任务
'''
import time
import json
import re
import traceback
import logging
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pyautogui
logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s-%(levelname)s]: %(message)s', datefmt="%H:%M:%S")

class GdufeMooc:
    ''' 广财慕课 '''

    def __init__(self, browser_lib, watch_time=15*60, max_video_number=3):
        self.browser_lib = browser_lib
        self.watch_time = watch_time
        self.max_video_number = max_video_number
        self.video_time_remain_list = []

    def into_main_page(self):
        self.browser_lib.open_url(
            'https://gdufe.xuetangonline.com')

    def login(self, file_path="src/cookies.json"):
        ''' 登录 '''
        self.browser_lib.add_cookies(file_path)

    def into_course(self, course_url):
        ''' 进入课程
        :param course_url: 课程的url
        :return: None
        '''
        self.browser_lib.open_url(course_url)

    def get_unfinished_tasks(self):
        ''' 获取未完成的任务(视频或作业或PPT等)
        :return: list
        '''
        #  <div data-v-6c1c5dda="" class="el-tooltip item f12 blue-color" aria-describedby="el-tooltip-9311" tabindex="0">未开始</div>
        filter_unfinished_tasks = []
        unfinished_tasks = self.browser_lib.get_elements({
            "type": "tag",
            "type_name": "div",
            "text_type": "text",
            "text": "进行中.*|未开始|未读|[0-9]+%"}, 10)
        if len(unfinished_tasks) != 0:
            for i in range(0, len(unfinished_tasks), 2):
                filter_unfinished_tasks.append(unfinished_tasks[i])
            return filter_unfinished_tasks
        return unfinished_tasks

    def get_task_title(self):
        ''' 获取任务标题
        :return: str
        '''
        #  <span data-v-3d9c166b="" class="text text-ellipsis">1.1.1课程介绍</span>
        task_title = self.browser_lib.get_element(
            #  {"type": "tag", "type_name": "span", "text_type": "text", "text": ".*随堂测试|第.*章作业|.*PPT.*|*"}, 10)
            {"type": "tag", "type_name": "span", "text_type": "text", "text": ".*随堂测试|.*作业|.*PPT.*|.*完成度.*|.*搭建问题"}, 10)
        if task_title:
            #  print("任务标题: ", task_title.text)
            return task_title.text
        return ""

    def get_video_title(self):
        ''' 获取视频标题
        :return: str
        '''
        #  <span data-v-3d9c166b="" class="text text-ellipsis">1.1.1课程介绍</span>
        video_title = self.browser_lib.get_element(
            #  {"type": "tag", "type_name": "span", "text_type": "text", "text": ".*随堂测试|第.*章作业|.*PPT.*|*"}, 10)
            {"type": "tag", "type_name": "span", "text_type": "text", "text": "[0-9].[0-9]"}, 10)
        if video_title:
            #  print("视频标题: ", video_title.text)
            return video_title.text
        return ""

    def into_task(self, unfinished_task):
        ''' 进入任务
        :param task: 需要进入的任务的网页元素对象
        :return: None
        '''
        if unfinished_task:
            unfinished_task.click()

    def judgment_task_type(self, task_title):
        ''' 判断任务类型
        :return: str
        '''
        #  "span", ".*PPT.*|.*随堂测试.*|.*作业.*|.*完成度.*"
        if re.match(".*PPT.*|.*随堂测试.*|.*作业.*|.*完成度.*|.*搭建问题", task_title):
            if re.match(".*完成度.*", task_title):
                return "视频"
            elif re.match(".*随堂测试.*|.*作业|.*搭建问题", task_title):
                return "作业"
            elif re.match("PPT", task_title):
                return "PPT"
            else:
                return "未知"
        return "未知"

    def perform_task(self, task_type):
        ''' 执行任务
        :param task_type: 任务类型
        :return: True || False
        '''
        if task_type == "视频":
            self.times_speed_playback(3)
            time.sleep(5)
            self.get_video_time()
        elif task_type == "作业":
            self.do_homework()
        else:
            time.sleep(5)

    def get_video_time(self):
        '''  获取视频剩余时间 '''
        script_code =\
            """
            let video = document.getElementsByTagName('video');
            let arr = [];
            for (let i=0; i<video.length; i++) {
                try {
                    arr.push(video[i].currentTime);
                    arr.push(video[i].duration);
                }catch(err){console.log(err)}
            }
            return arr
        """
        try:
            video_time = (self.browser_lib.browser.execute_script(script_code))
            if len(video_time) == 2:
                self.video_time_remain_list.append(
                    int(video_time[1] - video_time[0]))
            else:
                self.video_time_remain_list.append(self.watch_time)
        except:
            traceback.print_exc()
            self.video_time_remain_list.append(self.watch_time)

    def set_watch_time(self):
        ''' 设置视频等待时间 '''
        if len(self.video_time_remain_list) == 0:
            return
        self.watch_time = int(max(self.video_time_remain_list)/2)
        self.watch_time = self.watch_time + 30

    def times_speed_playback(self, speed=4):
        ''' 倍速播放视频
        :param speed: 多少倍速度(最高4倍)
        :return: None
        '''
        script_code = """
            function accelerate() {
            let video = document.getElementsByTagName('video');
            for (let i=0; i<video.length; i++) {
                try {
                    video[i].playbackRate = 4; // 倍速
                    if (!video[i].isPlay) {
                        video[i].play()
                    }
                }catch(err){console.log(err)}
            }
        }
            setInterval(accelerate, 100); // 定时播放，防止被js恢复原速或暂停
        """
        script_code = script_code.replace("4", str(speed))
        self.browser_lib.browser.execute_script(script_code)

    def do_homework(self):
        ''' 做作业
        :return: True || False
        '''
        task_title = self.get_task_title()
        answer_list = self.get_question_answer(task_title.strip())
        if len(answer_list) == 0:
            return False
        for answer in answer_list:
            try:
                self.switch_question(answer["index"])
                time.sleep(1)
                if self.answer_questions(int(answer["type"]), answer["answer"]):
                    self.submit_answer()
                time.sleep(1)
                self.browser_lib.browser.refresh()
                time.sleep(3)
            except:
                traceback.print_exc()
        return True

    def answer_questions(self, question_type, question_answer):
        ''' 回答问题
        :param question_type: 问题的类型
        :param question_answer: 问题的问题
        :return: True || False
        '''
        if question_type == 0:
            return self.single_topic_selection(question_answer)
        elif question_type == 1:
            return self.multiple_choice(question_answer)
        elif question_type == 2:
            return self.fills_up_topic(question_answer)
        elif question_type == 3:
            return self.true_false(question_answer)
        return False

    def switch_question(self, question_index):
        ''' 切换问题
        :param question_index: 切换到第几个问题
        :return: True || False
        '''
        question_element = self.browser_lib.get_element(
            {"type": "tag", "type_name": "div", "text_type": "text", "text": str(question_index)}, 10)
        if question_element:
            question_element.click()
            return True
        return False

    def get_question_answer(self, task_title):
        ''' 获取答案
        :param task_title: 任务标题
        :return: 数组
        '''
        with open('src/answer_data.json', 'r') as read_buff:
            answer_list = json.load(read_buff)
            #  print(cookies_list)
            for item in answer_list:
                if re.match(task_title, item["title"]):
                    return item["data"]
        return []

    def single_topic_selection(self, question_answer):
        ''' 选择题
        :param question_answer: 选择题答案 str
        :return: True || False
        '''
        single_topic = self.browser_lib.get_element(
            {"type": "tag", "type_name": "span", "text_type": "text", "text": question_answer}, 10)
        if single_topic:
            single_topic.click()
            return True
        return False

    def multiple_choice(self, question_answer):
        ''' 多选题
        :param question_answer: 多选题答案 list
        :return: True || False
        '''
        for answer_item in question_answer:
            single_topic = self.browser_lib.get_element(
                {"type": "tag", "type_name": "span", "text_type": "text", "text": answer_item}, 10)
            if single_topic:
                single_topic.click()
                time.sleep(0.3)
            else:
                return False
        return True

    def fills_up_topic(self, question_answer):
        ''' 填空题
        :param question_answer: 填空题答案 list
        :return: True || False
        '''
        #  <input data-v-44fb2176="" placeholder="输入答案" type="text" class="blank-item-dynamic" style="width: auto !important;">
        single_topic = self.browser_lib.get_elements(
            {"type": "tag", "type_name": "input", "text_type": "class", "text": "blank-item-dynamic"}, 10)
        for i in range(len(question_answer)):
            single_topic[i].send_keys(question_answer[i])
            time.sleep(0.3)
        return True

    def true_false(self, question_answer):
        ''' 判断题
        :param question_answer: 判断题答案 str
        :return: True || False
        '''
        result = self.browser_lib.get_element(
            {"type": "tag", "type_name": "ul", "text_type": "class", "text": "list-inline list-unstyled-radio"}, 10)
        result = result.find_elements_by_class_name("icon")
        if len(result) != 2:
            return False
        if question_answer == "T":
            result[0].click()
        elif question_answer == "F":
            result[1].click()
        return True

    def submit_answer(self):
        ''' 提交答案
        :return: None
        '''
        submit = self.browser_lib.get_element(
            {"type": "tag", "type_name": "span", "text_type": "text", "text": "提交.*剩余"}, 3)
        if submit:
            submit.click()


class BrowserLib:
    def __init__(self, driver):
        """启动浏览器参数化，默认启动chrome"""
        self.browser = driver
        self.debug_mode = False

    def dl(self, obj):
        ''' 调试日志
        :param obj: 需要输出的日志
        :return: None
        '''
        if self.debug_mode:
            logging.info(obj)

    def add_cookies(self, file_path):
        ''' 添加cookies
        :param file_name: 需要添加的cookies文件路径
        :return: True || False
        '''
        self.browser.delete_all_cookies()  # 删除cookies
        with open(file_path, 'r') as file_read_buff:
            # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookies_list = json.load(file_read_buff)
            for item in cookies_list:
                self.browser.add_cookie(item)
        self.browser.refresh()  # 刷新后cookie生效

    def get_elements(self, selector={"type": "tag", "type_name": "div", "text_type": "text", "text": ""}, _timeout=3):
        ''' 获取元素列表
        :param selector: 选择器
        :param _timeout: 超时时间
        :return: 元素数组 || 空数组
        '''
        try:
            end_time = time.time() + _timeout
            self.browser.implicitly_wait(_timeout)
            for _ in range(999999):
                if selector["type"] == "tag":
                    elements = self.browser.find_elements_by_tag_name(
                        selector["type_name"])
                elif selector["type"] == "id":
                    elements = self.browser.find_elements_by_id(
                        selector["type_name"])
                elif selector["type"] == "class":
                    elements = self.browser.find_elements_by_class_name(
                        selector["type_name"])
                elif selector["type"] == "name":
                    elements = self.browser.find_elements_by_name(
                        selector["type_name"])
                else:
                    return []
                element_list = []
                element_text = None
                for element in elements:
                    try:
                        if selector["text_type"] == "text":
                            element_text = element.get_attribute("innerText")
                        elif selector["text_type"] == "id":
                            element_text = element.get_attribute("id")
                        elif selector["text_type"] == "class":
                            element_text = element.get_attribute("class")
                        elif selector["text_type"] == "name":
                            element_text = element.get_attribute("name")
                        if not element_text:
                            continue
                        #  self.dl(element_text)
                        if re.match(selector["text"], element_text):
                            #  self.dl(element_text)
                            element_list.append(element)
                    except:
                        traceback.print_exc()
                if time.time() > end_time:
                    break
                if len(element_list) != 0:
                    break
            return element_list
        except:
            traceback.print_exc()

    def get_element(self, selector={"type": "tag", "type_name": "div", "text_type": "text", "text": ""}, _timeout=3):
        ''' 获取单个元素
        :param selector: 选择器
        :param _timeout: 超时时间
        :return: 元素 || None
        '''
        try:
            end_time = time.time() + _timeout
            self.browser.implicitly_wait(_timeout)
            for _ in range(999999):
                if selector["type"] == "tag":
                    elements = self.browser.find_elements_by_tag_name(
                        selector["type_name"])
                elif selector["type"] == "id":
                    elements = self.browser.find_elements_by_id(
                        selector["type_name"])
                elif selector["type"] == "class":
                    elements = self.browser.find_elements_by_class_name(
                        selector["type_name"])
                    #  elements = self.browser.find_element_by_class_name("xt-videomask")
                elif selector["type"] == "name":
                    elements = self.browser.find_elements_by_name(
                        selector["type_name"])
                else:
                    return None
                #  self.log(elements)
                element_text = None
                for element in elements:
                    #  self.log(element_text)
                    try:
                        if selector["text_type"] == "text":
                            element_text = element.get_attribute("innerText")
                        elif selector["text_type"] == "id":
                            element_text = element.get_attribute("id")
                        elif selector["text_type"] == "class":
                            element_text = element.get_attribute("class")
                        elif selector["text_type"] == "name":
                            element_text = element.get_attribute("name")
                        if not element_text:
                            continue
                        if re.match(selector["text"], element_text):
                            self.dl(element_text)
                            return element
                    except Exception as error:
                        traceback.print_exc()
                if time.time() > end_time:
                    break
            return None
        except Exception as error:
            print("获取元素出错:", error)

    def wait_text(self, _tag, _text, _timeout=10):
        """ 等待tag里的某个文本出现 """
        try:
            self.browser.implicitly_wait(_timeout)
            end_time = time.time() + _timeout
            for _ in range(999999):
                elements = self.browser.find_elements_by_tag_name(_tag)
                for element in elements:
                    #  self.log(element.get_attribute("innerText"))
                    if re.match(_text, element.get_attribute("innerText")):
                        return element
                if time.time() > end_time:
                    break
            return None
        except Exception as error:
            print("等待文本出错:", error)

    def open_url(self, _url, _timeout=20):
        ''' 打开url
        :param _url: 需要打开的url
        :return: None
        '''
        self.browser.implicitly_wait(_timeout)
        self.browser.get(_url)

    def current_window_handle(self):
        """浏览器handle"""
        return self.browser.current_window_handle

    def close_other_window(self, current_window):
        ''' 关闭其他窗口
        :param current_window: 需要保留的窗口句柄
        :return: None
        '''
        all_handle = self.browser.window_handles
        for handle in all_handle:
            if handle != current_window:
                self.browser.switch_to.window(handle)
                self.close()
        self.browser.switch_to.window(current_window)

    def switch_window_handle(self, handle_index):
        ''' 切换窗口
        :param handle_index: 第几个窗口，或者窗口句柄
        :return: None
        '''
        if not isinstance(handle_index, int):
            self.browser.switch_to.window(handle_index)
        else:
            all_handle = self.browser.window_handles
            if handle_index < len(all_handle):
                self.browser.switch_to.window(all_handle[handle_index])
            self.browser.switch_to.window(all_handle[len(all_handle)-1])

    def back(self):
        """返回之前的网页"""
        self.browser.back()

    def forward(self):
        """前往下一个网页"""
        self.browser.forward()

    def close(self):
        """关闭当前网页"""
        self.browser.close()

    def quit(self):
        """关闭所有网页"""
        self.browser.quit()

    def get_window_title(self):
        """获取title"""
        return self.browser.title


def main_process():
    ''' 主流程 
    1. 打开慕课网站
    2. 登录
    3. 循环完成所有课程
        1. 获取未完成的任务
        2. 执行任务
    '''
    chrome_options = Options()
    chrome_options.add_argument("--mute-audio")  # 静音
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_experimental_option(
        "excludeSwitches", ['enable-automation'])
    browser_lib = BrowserLib(webdriver.Chrome(options=chrome_options))
    browser_lib.debug_mode = False
    gdufe_mooc = GdufeMooc(browser_lib)
    course_list = [
        'https://gdufe.xuetangonline.com/pro/lms/8V4QCnLgeYZ/1423505/studycontent',
        'https://gdufe.xuetangonline.com/pro/lms/8V4QCnN2xSJ/1423519/studycontent',
    ]
    current_window = None  # 记录当前窗口
    task_count = 1
    task_title = ""
    task_type = "未知"
    unfinished_tasks = []
    i = 0
    # 流程开始
    gdufe_mooc.into_main_page()
    gdufe_mooc.login("src/chang.json")
    while i < len(course_list):
        gdufe_mooc.into_course(course_list[i])
        current_window = browser_lib.current_window_handle()
        time.sleep(1)  # 等待任务加载
        unfinished_tasks = gdufe_mooc.get_unfinished_tasks()
        for j in range(0, len(unfinished_tasks)):
            gdufe_mooc.into_task(unfinished_tasks[j])
            time.sleep(0.5)  # 等待标签打开
            browser_lib.switch_window_handle(99)  # 切换到最后一个窗口
            time.sleep(0.5)
            task_title = gdufe_mooc.get_task_title()
            task_type = gdufe_mooc.judgment_task_type(task_title)
            print("任务标题: ", task_title)
            print("任务类型: ", task_type)
            gdufe_mooc.perform_task(task_type)
            if task_type != "视频":
                browser_lib.close()
                browser_lib.switch_window_handle(current_window)  # 切回课程页
                continue
            print("视频标题: ", gdufe_mooc.get_video_title())
            browser_lib.switch_window_handle(current_window)  # 切回课程页
            time.sleep(0.5)  # 等待切换
            if task_count % gdufe_mooc.max_video_number == 0:
                gdufe_mooc.set_watch_time()
                print("观看视频时间: ", gdufe_mooc.watch_time)
                time.sleep(gdufe_mooc.watch_time)
                gdufe_mooc.video_time_remain_list = []
                browser_lib.close_other_window(current_window)
            task_count += 1
            time.sleep(0.5)
        unfinished_tasks = gdufe_mooc.get_unfinished_tasks()
        print("剩余未完成数量:", len(unfinished_tasks))
        if len(unfinished_tasks) != 0:
            i -= 1
        i += 1
    time.sleep(5)  # 等待5秒后退出


main_process()
