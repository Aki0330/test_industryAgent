# import sys
# sys.path.append(r"D:\Python\Lib\site-packages")

from csmarapi.CsmarService import CsmarService
from csmarapi.ReportUtil import ReportUtil
from dotenv import load_dotenv
import os

import pandas as pd

load_dotenv()

account = os.getenv("CSMAR_ACCOUNT")
password = os.getenv("CSMAR_PASSWORD")

csmar = CsmarService()
csmar.login(account, password)

table_name = "AI_Paspv01"

# 先获取字段列表
fields = csmar.getListFields(table_name)
columns = [f['field'] for f in fields]  # 提取字段名列表

print(f"查询字段共 {len(columns)} 个，字段示例：{columns[:5]}")

# 设置查询条件为空，表示查询所有数据
condition = ""

# 根据表时间区间决定是否加时间限制（非必需）
# 这里假设无时间限制，若有时间限制可加，如：start_time = "2009-05-01", end_time = "2017-10-01"
start_time = None
end_time = None

# 一次最多200,000条，先试着直接查，如果超限后续分页
data = csmar.query_df(columns, condition, table_name, start_time, end_time)

print(f"查询到数据条数：{len(data)}")
print(data.head())

# 保存为csv文件，使用utf-8-sig防止Excel乱码
data.to_csv(f"{table_name}.csv", index=False, encoding="utf-8-sig")


# industry_data_json = csmar.query(
#     ['Stkcd', 'InduCode', 'InduName'],
#     "InduStandard = '中证'",
#     'LC_InduStandard'
# )
# print(industry_data_json)


# industry_data = csmar.query_df(
#     ['Stkcd', 'InduCode', 'InduName', 'InduStandard', 'EndDate'],
#     "InduStandard = '中证'",
#     'LC_InduStandard'
# )

# if industry_data is None:
#     print("未获取到行业数据，请检查请求频率或条件。")
# else:
#     ev_keywords = ['新能源', '电动', '锂电', '充电', '整车', '电池']
#     ev_companies = industry_data[industry_data['InduName'].str.contains('|'.join(ev_keywords), na=False)]
#     print(ev_companies[['Stkcd', 'InduName']].drop_duplicates())


# # 模糊匹配行业名称中含有“新能源汽车”、“电动汽车”、“电池”、“充电”等关键字
# ev_keywords = ['新能源', '电动', '锂电', '充电', '整车', '电池']
# ev_companies = industry_data[industry_data['InduName'].str.contains('|'.join(ev_keywords), na=False)]

# print(ev_companies[['Stkcd', 'InduName']].drop_duplicates())

# #stk_list = ev_companies['Stkcd'].unique().tolist()

