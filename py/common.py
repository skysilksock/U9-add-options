from abc import ABC, abstractmethod
import pandas as pd
import os


class ExcelReader:
    @staticmethod
    def get_data(file_path: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        读取excel文件，返回新增零配件和回仓零配件的DataFrame
        :param file_path:
        :return:
        """
        df = pd.read_excel(file_path)
        part_add_index = df[df['序号'] == '新增零配件'].index[0]
        part_back_index = df[df['序号'] == '回仓零配件'].index[0]
        part_add_df = df.iloc[part_add_index + 1:part_back_index]
        part_back_df = df.iloc[part_back_index + 1:]
        return part_add_df, part_back_df

    @staticmethod
    def get_figure_number(file_path: str) -> tuple[list, list]:
        """
        读取excel文件，返回新增零配件和回仓零配件的图号列表
        :param file_path:
        :return:
        """
        add_df, back_df = ExcelReader.get_data(file_path)
        # 去除NaN值
        add_df = add_df[add_df['图号/编码'].notna()]
        back_df = back_df[back_df['图号/编码'].notna()]
        return add_df['图号/编码'].tolist(), back_df['图号/编码'].tolist()


if __name__ == '__main__':
    A = ExcelReader()
    print(ExcelReader.get_data('../U9Excel/1786.xlsx'))
    print(ExcelReader.get_data('../U9Excel/1778.xls'))
    a, b = ExcelReader.get_figure_number('../U9Excel/1786.xlsx')
    print(f"表格1786的新增零配件：{a}\n回仓零配件：{b}")
    a, b = ExcelReader.get_figure_number('../U9Excel/1778.xls')
    print(f"表格1778的新增零配件：{a}\n回仓零配件：{b}")
    print(','.join(b))