"""
工作流程：
1. 查找机型批号和对应选配项
2. 根据选配项在excel文件中找到对应的新增与回仓
3. 使用selenium模拟浏览器操作，登录U9系统
4. 按照新增与回仓顺序，执行操作
"""
import time

# 导入所需模块
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import pandas as pd
from py.beautifulSoup import ProduceListParser
from py.optionDeal import OptionDeal

# 配置 edge
options = webdriver.EdgeOptions()
options.use_chromium = True

# 创建服务
service = webdriver.EdgeService(executable_path='edgedriver_win64/msedgedriver.exe')

# 创建浏览器
driver = webdriver.Edge(service=service, options=options)
# 创建键盘操作对象
ac = ActionChains(driver)

# driver配置
driver.maximize_window()
driver.implicitly_wait(20)

iframe_num = 1

def counter_decorator(func):
    def wrapper(*args, **kwargs):
        wrapper.counter += 1
        return func(*args, **kwargs)
    wrapper.counter = 0
    return wrapper

def login_U9():
    """
    登录U9页面
    :return:
    """
    # 打开U9系统登录页面
    # cookies = [{'domain': '79.8.5.218', 'httpOnly': True, 'name': 'ASP.NET_SessionId', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'uux2k4cqlviddoenej5url0y'}, {'domain': '79.8.5.218', 'expiry': 1750655054, 'httpOnly': True, 'name': '.ASPXANONYMOUS', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'B-Mt5zAQRQP1QL7z2Xno6af9Hof4T5vtOFq25lQeL0XbEvZuRmFzJpBnd25_fbOuuZPxNu18NtN3QMI28omPqgWaqRFXxHPVv1S4DJm2wfAOlQ3a1QFcjizbVgK5ygUQ2GY33g2'}]
    driver.get('http://79.8.5.218/U9/mvc/login/index')

    # 输入用户名密码
    input_username = driver.find_element(By.CSS_SELECTOR, '#userName')
    input_username.send_keys('676')
    input_password = driver.find_element(By.CSS_SELECTOR, '#password')
    input_password.send_keys('@242116')

    # 点击登录按钮
    login_button = driver.find_element(By.CSS_SELECTOR, '#loginBtn')
    login_button.click()

def open_manifest():
    """

    :return:
    """
    # 菜单按钮
    menu_btn = driver.find_element(By.CSS_SELECTOR, '#nav-vertical')
    menu_btn.click()
    # 生产制造按钮
    manufacturing_btn = driver.find_element(By.CSS_SELECTOR, 'body > div.modules > div.modules-list > div:nth-child(3) > h3')
    manufacturing_btn.click()
    # 生产管理按钮
    produce_manage_btn = driver.find_element(By.CSS_SELECTOR, 'body > div.modules > div.modules-list > div:nth-child(3) > dl > dd:nth-child(2) > div.erji')
    produce_manage_btn.click()
    # 生产订单a标签
    produce_order_a = driver.find_element(By.XPATH, '/html/body/div[9]/div[2]/div[3]/dl/dd[2]/div[2]/ul/li[1]/ul/li[3]/a')
    produce_order_a.click()
    # 进入生产订单页面
    produce_order_page = driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[2]/div[2]/iframe')
    driver.switch_to.frame(produce_order_page)
    # 点击列表
    list_btn = driver.find_element(By.CSS_SELECTOR, '#u_M_p0_BtnList')
    list_btn.click()
    # 进入生产定单列表页面
    driver.switch_to.default_content() # 退出iframe

@counter_decorator
def get_model_list(batch_num):
    produce_order_list_page = driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[3]/div[2]/iframe')  # 生产订单列表页面
    driver.switch_to.frame(produce_order_list_page)
    # 查询按钮
    query_btn = driver.find_element(By.CSS_SELECTOR, '#u_M_p0_OnLookCase_button')
    query_btn.click()
    # 进入查询页面
    driver.switch_to.default_content()  # 退出iframe
    query_page = driver.find_element(By.CSS_SELECTOR, '.layui-layer-load')
    driver.switch_to.frame(query_page)
    # 输入批号
    input_patch = driver.find_element(By.XPATH, '//*[@id="u_S_S1_Filter0_filterCtrl_DemandCode__ddlEnumCtrl1_textbox"]')
    # input_patch.clear()  # 不清空的话会保留之前输入的批号
    input_patch.send_keys(batch_num)
    commit_btn = driver.find_element(By.XPATH, '//*[@id="u_S_S1_OnFind_button"]')
    # commit_btn.click() # 突然莫名奇妙不起作用了
    ac.move_to_element(commit_btn).click().perform()
    driver.switch_to.default_content()

def checkIsSearch(model_status: dict) -> bool:
    model_list = set(map(lambda x:x.split('/')[0],model_status.keys()))
    return len(model_list) == 1


def deal_models(batch_num):
    while True:
        print(get_model_list.counter, "wait")
        time.sleep(get_model_list.counter)  # 如果不进行等待的话数据库搜索的信息还未更新到DOM，会查到为搜索前的信息
        # 进入生产订单列表页面
        produce_order_list_page = driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[3]/div[2]/iframe')  # 生产订单列表页面
        driver.switch_to.frame(produce_order_list_page)
        # 获取并解析table标签
        table = driver.find_element(By.CSS_SELECTOR, '.dataGridMainBody table')
        html_text = table.get_attribute('outerHTML')
        P = ProduceListParser(html_text)
        model_status = P.parse_small()
        print(checkIsSearch(model_status))
        if not checkIsSearch(model_status):
            driver.switch_to.default_content()
            get_model_list(batch_num)
            continue
        else:
            driver.switch_to.default_content()
            for k, v in model_status.items():  # k为机台号，v为审核状态 [k, v] = [D065365/01#, '已核准']
                deal_model(k, v, )
                raise Exception("测试")


def deal_model(model, state, part_to_add: list[str]=None, part_to_back: list[str]=None):
    """
    css: '[data-ca="{\'value\':\'{0}\'}"]'.format(model)
    :param model:
    :return:
    """
    # state = "开立" # 暂时改变状态进行测试
    S = OptionDeal(driver, model, state, part_to_add, part_to_back)
    S.option_deal()

    # # 进入生产订单列表页面
    # produce_order_list_page = driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[3]/div[2]/iframe')  # 生产订单列表页面
    # driver.switch_to.frame(produce_order_list_page)
    # # 双击机台号
    # main_table = driver.find_element(By.CSS_SELECTOR, '.dataGridMainBody table > tbody')
    # test_btn = main_table.find_element(By.CSS_SELECTOR, f"[title='{model}']")
    # ac.move_to_element(test_btn).double_click().perform()
    # # 重新进入生产订单页面，切换iframe
    # time.sleep(2)
    # driver.switch_to.default_content()
    # produce_order_page = driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[3]/div[2]/iframe')
    # driver.switch_to.frame(produce_order_page)
    # # 点击备料按钮
    # prepare_btn = driver.find_element(By.CSS_SELECTOR, "[value='备料']")
    # print(prepare_btn.get_attribute('outerHTML'))
    # prepare_btn.click()
    # time.sleep(200)




if __name__ == '__main__':
    login_U9()
    open_manifest()
    get_model_list('D065365')
    deal_models('D065365')
