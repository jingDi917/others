
import json
import os

# 密码
CHECK_CODE = "dingjing"

# 数据
## schemas 公共数据
DATA_INDEX_NAME = 'index'
DATA_HUNDREDS_NAME = 'Hundreds'
DATA_TENS_NAME = 'tens'
DATA_ONES_NAME = 'ones'
DATA_SCHEMAS = [DATA_INDEX_NAME, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME]

ADD_DATA_ACCOUNT_INDEX = 0
INIT_DATA_STATUS_ACCOUNT_INDEX = 1

## 库路径
RAW_DATA_FILE = './c_3d/datas/raw_data.txt'
ACCOUNT_FILE = './c_3d/datas/account.txt'
BASE_PROB_FILE = './c_3d/datas/base_prob.txt'
FILTER_NUMBER_FILE = './c_3d/datas/filter_number.txt'
ENHANCE_NUMBER_FILE = './c_3d/datas/enhance_number.txt'
DATA_STATUS_FILE = './c_3d/datas/data_status.txt'

# 变量名
PAIR_PROB = 'pair_prob'
TUPLE_PROB = 'tuple_prob'
ODD_EVEN_RATIO = 'odd_even_ratio'
SUM_PROB = 'sum_prob'
DIFF_PROB = 'diff_prob'
NUMBER = 'number'
POSITION_RANGE = 'position_range'
POSITION_RELATION = 'position_relation'


# 初始化
INIT_NUMBER_OF_DATA = 100
INIT_SUM_BREAK_THRESHOLD = 0.6
INIT_DIFF_BREAK_THRESHOLD = 0.6

# 超参数
PDF_ADD_FATOR = 0   # 加性因子，用于提升高频数字的出现概率
PDF_TIME_FACTOR = 8     # 乘积因子
PDF_DECAL_FACTOR = 0.18

FIRST_FILTER_PAIR_THRESHOLD = 0.37
SECOND_FILTER_PAIR_THRESHOLD = 0.4

IGNORE_SUM_THRESHOLD = 0.03
ENHANCE_SUM_THRESHOLD = 0.2
IGNORE_DIFF_THRESHOLD = 0.06
ENHANCE_DIFF_THRESHOLD = 0.2

FINAL_DROP_RATIO = 0.45


# 组合阈值
AUXILIAY_RANGE = 100
FILTER_THRESHOLD = 0.65 # 调节这个参数，能减少3的干数，实际上增加了范围
ENHANCE_THRESHOLD = 0.7

# 一会对比下实际数据和均值的差距


# 代码

class WriteBaseData:
    @classmethod
    def writeAccounts(cls, account_array):
        with open(ACCOUNT_FILE, 'w') as fp:
            for year, index in account_array:
                fp.write(f"{year}\t{index:03d}\n")

    @classmethod
    def writeJsonData(cls, file_name, data):
        # 保存到文件
        with open(file_name, 'w') as fp:
            json.dump(data, fp, indent=4)

    @classmethod
    def appendRawData(cls, raw_datas):
        fp = open(RAW_DATA_FILE, 'a')
        for line in raw_datas:
            fp.write(line)
        fp.close()

    @classmethod
    def writeAllRawData(cls, raw_datas):
        with open(RAW_DATA_FILE, 'w') as fp:
            for line in raw_datas:
                fp.write(line)
            fp.close()

class GetBaseData:
    @classmethod
    def getAccounts(cls):
        indexArray = []
        try:
            with open(ACCOUNT_FILE, 'r') as fp:
                content = fp.read()
                for line in content.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    current_year, current_index = map(int, line.split('\t'))
                    indexArray.append((current_year, current_index))
            return indexArray
        except FileNotFoundError:
            raise FileNotFoundError(f"账号文件 {ACCOUNT_FILE} 不存在，请先创建。")
    @classmethod
    def getBaseProb(cls):
        try:
            with open(BASE_PROB_FILE, 'r') as fp:
                content = fp.read()
                return json.loads(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"基础概率文件 {BASE_PROB_FILE} 不存在，请先调用init_prob。")
    
    @classmethod
    def getRawData(cls, data_index = None):
        try:
            data = []
            with open(RAW_DATA_FILE, 'r') as fp:
                content = fp.read()
                lines = content.split('\n')
                for line in lines:
                    line = line.strip()
                    data.append(dict(zip(DATA_SCHEMAS, line.split('\t'))))
                if data_index is None:
                    return data
                index = 0
                for record in data:
                    if record[DATA_INDEX_NAME] == data_index:
                        break
                    index += 1
                return data[:index]
        except FileNotFoundError:
            raise FileNotFoundError(f"原始数据文件 {RAW_DATA_FILE} 不存在，请先调用创建。")
        
    @classmethod
    def getDataStatus(cls):
        try:
            with open(DATA_STATUS_FILE, 'r') as fp:
                content = fp.read()
                return json.loads(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"基础概率文件 {DATA_STATUS_FILE} 不存在，请先调用init_data。")
    
    @classmethod
    def getFilterNumberMap(cls):
        try:
            with open(FILTER_NUMBER_FILE, 'r') as fp:
                content = fp.read()
                return json.loads(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"过滤数据文件 {FILTER_NUMBER_FILE} 不存在，请先调用init_prob。")
        
    @classmethod
    def getEnhanceNumberMap(cls):
        try:
            with open(ENHANCE_NUMBER_FILE, 'r') as fp:
                content = fp.read()
                return json.loads(content)
        except FileNotFoundError:
            raise FileNotFoundError(f"过滤数据文件 {ENHANCE_NUMBER_FILE} 不存在，请先调用init_prob。")

class BaseCommonFunc:
    @classmethod
    def splitDataIndex(cls, data_index):
        if not isinstance(data_index, str):
            raise ValueError(f"数据索引必须是字符串: {data_index} type: {type(data_index)}")
        if len(data_index) != 5:
            raise ValueError(f"数据索引必须是5位: {len(data_index)}")
        try:
            int(data_index[:2])  # 检查年份部分是否为数字
            int(data_index[2:])  # 检查期号部分是否为数字
        except ValueError:
            raise ValueError(f"数据索引格式错误: {data_index}，必须是YYYYDDD格式，其中YYYY为年份，DDD为期号")
        return int(data_index[:2]), int(data_index[2:])  # 返回年份和期号   

    @classmethod
    def addIndex(cls, current_year, current_index):
        current_index += 1
        if current_index > 352:
            current_index = 1
            current_year += 1
        return current_year, current_index