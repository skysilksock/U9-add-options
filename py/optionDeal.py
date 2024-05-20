import os
import sys
from abc import ABC, abstractmethod
import time
import warnings
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

sys.path.insert(0, os.getcwd() + "\py")
from beautifulSoup import ProduceListParser


def printElement(element):
    print(element.get_attribute('outerHTML'))

class OptionDealStrategy(ABC):
    def __init__(self, driver: webdriver, model: str):
        self.driver = driver
        self.ac = ActionChains(driver)
        self.model = model

    @abstractmethod
    def part_add(self, part_to_add: list[str]):
        pass

    @abstractmethod
    def part_back(self, part_to_back: list[str]):
        pass


class OptionDealDirectStrategy(OptionDealStrategy):
    def part_add(self, part_to_add: list[str]):
        """
        进入备料iframe->点击任意单元格->点击新增按钮->等待sql查询？->
        ->点击料号搜索->
        :param part_to_add:
        :return:
        """
        self.prepare_to_change()
        # 进入备料页面
        prepare_page = self.driver.find_element(By.CSS_SELECTOR, '.layui-layer-load')
        self.driver.switch_to.frame(prepare_page)
        table = self.driver.find_element(By.XPATH, '//*[@id="u_S_S1_DataGrid8_MainBody"]/table/tbody')
        # 点击第一行料品单元格
        cell = table.find_element(By.XPATH, 'tr/td[11]')
        cell.click()
        add_btn = self.driver.find_element(By.CSS_SELECTOR, "[title='Ctrl+Insert']")
        add_btn.click()
        # 点击新增按钮 需要等待页面DOM元素变化
        time.sleep(1)
        add_btn = table.find_element(By.CSS_SELECTOR, 'tr:last-child')
        add_btn.click()
        # 点击搜索按钮
        search_btn = add_btn.find_element(By.CSS_SELECTOR, 'button')
        search_btn.click()
        # 切换iframe
        self.driver.switch_to.default_content()
        material_page = self.driver.find_element(By.CSS_SELECTOR, '#layui-layer-iframe3')
        self.driver.switch_to.frame(material_page)
        # 点击查询按钮进行批量添加
        query_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_QryButton_button')
        query_btn.click()
        # 切换iframe
        self.driver.switch_to.default_content()
        query_page = self.driver.find_element(By.CSS_SELECTOR, '#layui-layer-iframe4')
        self.driver.switch_to.frame(query_page)
        # 输入原编码
        input_box = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_Filter0_filterCtrl_Code1_ReadOnlyValue_textbox')
        print(part_to_add)
        old_code = self.add_format_U9(part_to_add)
        input_box.send_keys(old_code)
        # 点击确定进行搜索
        commit_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_OnFind_button')
        commit_btn.click()
        # 切换ifr
        self.driver.switch_to.default_content()
        material_page = self.driver.find_element(By.CSS_SELECTOR, '#layui-layer-iframe3')
        self.driver.switch_to.frame(material_page)
        # test = self.driver.find_element(By.CSS_SELECTOR, 'html')
        # printElement(test)
        # 判断找到的零件数量是否与输入一致
        pass
        # 点击全选
        time.sleep(1)
        check_all = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_DataGrid_MainBody > table > thead > tr > td:nth-child(1) > input[type=checkbox]')
        # print("---------------------------")
        printElement(check_all)
        check_all.click()
        # 点击确定
        # time.sleep(1)
        commit_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_ConfirmButton')
        printElement(commit_btn)
        commit_btn.click()
        time.sleep(100)

    def part_back(self, part_to_back: list[str]):
        self.prepare_to_change()
        pass

    def prepare_to_change(self):
        """
        对于直接更改而言，无论是新增还是回仓，都需要经过重算备料->点击备料的步骤
        :return:
        """
        # 进入生产订单列表页面
        produce_order_list_page = self.driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[3]/div[2]/iframe')  # 生产订单列表页面
        self.driver.switch_to.frame(produce_order_list_page)
        # 双击机台号
        main_table = self.driver.find_element(By.CSS_SELECTOR, '.dataGridMainBody table > tbody')
        test_btn = main_table.find_element(By.CSS_SELECTOR, f"[title='{self.model}']")
        self.ac.move_to_element(test_btn).double_click().perform()
        # 此时生产订单列表页面变为生产定单页面，切换iframe
        time.sleep(2)
        self.driver.switch_to.default_content()
        produce_order_page = self.driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[3]/div[2]/iframe')
        self.driver.switch_to.frame(produce_order_page)
        """
        # 重算备料（耗时过长，测试时先注释）
        options_to_recalculate_btn = self.driver.find_element(By.CSS_SELECTOR, "#u_M_p0_DDBtnOperation_button")
        options_to_recalculate_btn.click()
        recalculate_btn = self.driver.find_element(By.XPATH, '//*[@id="ss013"]/td[2]')
        recalculate_btn.click()
        time.sleep(15) # 等待重算备料
        """
        # 点击备料按钮
        prepare_btn = self.driver.find_element(By.CSS_SELECTOR, "[value='备料']")
        prepare_btn.click()
        time.sleep(5) # 等待备料加载，（可以改为隐式等待）
        self.driver.switch_to.default_content()

    @staticmethod
    def add_format_U9(part_to_add: list[str]) -> str:
        return ','.join(part_to_add)


class OptionDealIndirectStrategy(OptionDealStrategy):
    def part_add(self, part_to_add: list[str]):
        self.prepare_to_change()
        pass

    # 没有回仓更改功能
    def part_back(self, part_to_back: list[str]):
        warnings.warn("当使用工程更改单进行选配项时，无法使用回仓功能")

    def prepare_to_change(self):
        """
        对于通过工程更改单方式修改而言，需要先打开工程更改单界面
        :return:
        """
        # 菜单按钮
        menu_btn = self.driver.find_element(By.CSS_SELECTOR, '#nav-vertical')
        self.ac.move_to_element(menu_btn).perform()
        # 生产制造按钮
        manufacturing_btn = self.driver.find_element(By.CSS_SELECTOR, 'body > div.modules > div.modules-list > div:nth-child(3) > h3')
        manufacturing_btn.click()
        # 生产管理按钮
        produce_manage_btn = self.driver.find_element(By.CSS_SELECTOR, 'body > div.modules > div.modules-list > div:nth-child(3) > dl > dd:nth-child(2) > div.erji')
        produce_manage_btn.click()
        # 生产订单变更单a标签
        produce_order_change_a = self.driver.find_element(By.XPATH, '/html/body/div[9]/div[2]/div[3]/dl/dd[2]/div[2]/ul/li[1]/ul/li[4]/a')
        produce_order_change_a.click()
        # 进入生产订单变更单页面
        produce_order_page = self.driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[4]/div[2]/iframe')
        self.driver.switch_to.frame(produce_order_page)
        # 设置单据类型
        order_type_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_M_p0_refDocType_button')
        order_type_btn.click()
        self.driver.switch_to.default_content()  # 退出iframe
        order_type_page = self.driver.find_element(By.CSS_SELECTOR, '.layui-layer-load')
        self.driver.switch_to.frame(order_type_page)
        # 提交
        commit_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_ConfirmButton')
        commit_btn.click()
        # 设置变更订单机型号
        self.driver.switch_to.default_content()  # 切换iframe，退回生产订单变更单界面
        produce_order_page = self.driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[4]/div[2]/iframe')
        self.driver.switch_to.frame(produce_order_page)
        number_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_M_p0_refMODocNo_button')
        number_btn.click()
        self.driver.switch_to.default_content()  # 退出iframe
        order_number_page = self.driver.find_element(By.CSS_SELECTOR, '.layui-layer-load')
        self.driver.switch_to.frame(order_number_page)
        # 解析table标签
        table = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_DataGrid_MainBody > table')
        html_text = table.get_attribute("outerHTML")
        P = ProduceListParser(html_text)
        self.model = "D065365/09#" # 测试使用
        x, y = P.search_index_by_name(self.model)
        cell = table.find_element(By.CSS_SELECTOR, f'tbody > tr:nth-child({x})')
        cell.click()
        # 提交
        commit_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_S_S1_ConfirmButton')
        commit_btn.click()
        self.driver.switch_to.default_content()  # 切换iframe，退回生产订单变更单界面
        produce_order_page = self.driver.find_element(By.XPATH, '/html/body/div[8]/div/div/div[2]/div[4]/div[2]/iframe')
        self.driver.switch_to.frame(produce_order_page)
        reason_input = self.driver.find_element(By.CSS_SELECTOR, "#u_M_p0_tbModifyReason_textbox")
        reason_input.send_keys(f"选配项更改")  # 之后传入对应选配项信息
        # 点击快速创建按钮创建更改单
        time.sleep(1)
        create_btn = self.driver.find_element(By.CSS_SELECTOR, '#u_M_p0_btnQuickCreate_button')
        self.ac.move_to_element(create_btn).click().perform()
        time.sleep(2)
        self.driver.switch_to.default_content()  # 切换iframe，退回生产订单变更单界面
        # 切换iframe，点击备料
        order_page = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.layui-layer-load'))
        )
        self.driver.switch_to.frame(order_page)
        # order_page = self.driver.find_element(By.CSS_SELECTOR, '.layui-layer-load')
        # self.driver.switch_to.frame(order_page)
        prepare_btn = self.driver.find_element(By.CSS_SELECTOR, "[value='备料']")
        prepare_btn.click()
        self.driver.switch_to.default_content()  # 切换iframe，退回生产订单变更单界面


class OptionDeal:
    def __init__(self, driver: webdriver, model:str, state: str, part_to_add: list[str], part_to_back: list[str]):
        self.driver = driver
        self.model = model
        self.state = state
        self.part_to_add = part_to_add
        self.part_to_back = part_to_back
        # 如果是开立（开始立项），则直接执行
        self.direct_state = ["开立", "核准中"]
        self.direct_strategy = OptionDealDirectStrategy(driver, model)
        # 如果是已核准或开工，则通过工程更改单执行
        self.indirect_state = ["已核准", "开工"]
        self.indirect_strategy = OptionDealIndirectStrategy(driver, model)

    def option_deal(self) -> None:
        """
        选配项添加和回仓操作的统一接口
        :return:
        """
        self.part_add(self.part_to_add)
        self.part_back(self.part_to_back)

    def part_add(self, part_to_add: list[str]) -> None:
        """
        如果状态为已核准或开工，则通过工程更改单执行选配项添加，即间接执行
        如果状态为开立，则直接执行选配项添加
        :return:
        """
        if self.state in self.direct_state:
            self.direct_strategy.part_add(part_to_add)
        elif self.state in self.indirect_state:
            self.indirect_strategy.part_add(part_to_add)
        else:
            raise ValueError(f"状态错误,您提供的{self.state}机型状态未定义")

    def part_back(self, part_to_back: list[str]) -> None:
        """
        如果状态为已核准或开工，则通过工程更改单执行回仓操作，即间接执行，在相关类中没有实现相关操作，会抛出异常
        如果状态为开立，则直接执行回仓操作
        :return:
        """
        if self.state in self.direct_state:
            self.direct_strategy.part_back(part_to_back)
        elif self.state in self.indirect_state:
            self.indirect_strategy.part_back(part_to_back)
        else:
            raise ValueError(f"状态错误,您提供的{self.state}机型状态未定义")

if __name__ == '__main__':
    """
    """