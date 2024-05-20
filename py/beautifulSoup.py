from collections import defaultdict
from bs4 import BeautifulSoup


class ProduceListParser:
    """
    用于解析生产订单页面包含了指定生产批号对应的所有机台号表格
    """
    def __init__(self, html_text: str) -> None:
        """
        初始化
        :param html_text: 需要解析的html文本
        """
        soup = BeautifulSoup(html_text, 'html.parser')
        self.table = soup.find('table')
        self.tbody = soup.find('tbody')

    def parse(self) -> defaultdict:
        """
        将整个表格解析为字典返回
        :return: 字典，键为表格抬头，值为表格值
        """
        title = []
        models = defaultdict(list)
        rows = self.table.find_all('tr')[:-1]  # 最后一行是汇总数据，不用处理
        for i, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])  # th表示表头单元格，td表示数据单元格
            if i == 0:
                for cell in cells:
                    title.append(cell.text.strip())
                    models[cell.text.strip()] = []
            else:
                for j, cell in enumerate(cells):
                    f_type = title[j]
                    models[f_type].append(cell.text.strip())
        del models['']  # 删除第一栏多选框列
        del models['*']  # 删除第二栏不知道什么列
        return models

    def parse_small(self) -> dict:
        """
        提取需要的每台机器对应的审核状态
        :return: 字典，键为机台号，值为审核状态
        """
        models = self.parse()
        ans = dict()
        for model, state in zip(models['机台号'], models['单据状态']):
            ans[model] = state
        del ans['机台号']  # 为了让main判断是否数据库已进行搜索，去掉机台号字段判断其它字段是否键前缀相同
        return ans

    def search_index_by_name(self, name: str) -> tuple[int, int]:
        """
        给定一个字符串，返回在给定table的tbody标签中第一次出现的坐标位置，索引从1开始
        :param name:
        :return:
        """
        rows = self.tbody.find_all('tr')
        for i, row in enumerate(rows):
            cells = row.find_all(['th', 'td'])  # th表示表头单元格，td表示数据单元格
            for j, v in enumerate(cells):
                if v.text.strip() == name:
                    return i + 1, j + 1
        raise KeyError(f"表格中不存在{name}元素")

