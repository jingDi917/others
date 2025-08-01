from .common import ADD_DATA_ACCOUNT_INDEX, CHECK_CODE, DATA_STATUS_FILE, INIT_DATA_STATUS_ACCOUNT_INDEX
from .common import GetBaseData, WriteBaseData, BaseCommonFunc
from .common import DATA_INDEX_NAME, DATA_HUNDREDS_NAME, DATA_TENS_NAME, DATA_ONES_NAME
from .strategy import Predictor
from .data_status import DataOperator
import traceback


START_YEAR = 2024
START_INDEX = 250


def splitData(input_str):
    return input_str[0], input_str[1], input_str[2]


def addData():
    try:
        account_array = GetBaseData.getAccounts()
        current_year, current_index = account_array[ADD_DATA_ACCOUNT_INDEX][0], account_array[ADD_DATA_ACCOUNT_INDEX][1]
        raw_data_list = []
        while True:
            input_str = input("请输入数据(输入exit退出): ")
            if input_str == 'exit':
                break
            if not input_str.isdigit() or len(input_str) != 3:
                print("期号必须是数字")
                continue
            hundreds, tens, ones = splitData(input_str)
            if hundreds not in '0123456789' or tens not in '0123456789' or ones not in '0123456789':
                print("输入必须是数据")
                continue    
            epochIndex = f"{current_year}{current_index:03d}"
            current_year, current_index = BaseCommonFunc.addIndex(current_year, current_index)
            raw_data_list.append(f"{epochIndex}\t{hundreds}\t{tens}\t{ones}")

        # 更新账号文件
        account_array[ADD_DATA_ACCOUNT_INDEX] = (current_year, current_index)
        WriteBaseData.writeAccounts(account_array)
        WriteBaseData.appendRawData(raw_data_list)

    except FileNotFoundError as e:
        raise FileNotFoundError(f"文件操作失败: {e}")
    
def addData(period, hundreds, tens, ones, check_code):
    """添加期数数据"""
    # 1. 校验码检查
    if check_code != CHECK_CODE:
        return 1, "验证码错误"
    
    try:
        # 2. 数据格式检查
        hundreds, tens, ones = str(hundreds), str(tens), str(ones)
        if not (hundreds.isdigit() and tens.isdigit() and ones.isdigit()):
            return 2, "数据格式错误! 必须输入0-9之间的数字!"
        
        # 3. 数据处理
        current_year, current_index = BaseCommonFunc.splitDataIndex(period)
        hundreds = int(hundreds)
        tens = int(tens)
        ones = int(ones)
        
        # 4. 准备数据
        epochIndex = f"{current_year}{current_index:03d}"
        raw_data = [f"{epochIndex}\t{hundreds}\t{tens}\t{ones}\n"]
        record = {
            DATA_INDEX_NAME: epochIndex,
            DATA_HUNDREDS_NAME: hundreds,
            DATA_TENS_NAME: tens,
            DATA_ONES_NAME: ones,
        }
        
        # 5. 更新数据
        cur_data_status = GetBaseData.getDataStatus()
        base_prob = GetBaseData.getBaseProb()
        DataOperator.updateRtDataStatus(record, cur_data_status, base_prob)
        
        # 6. 更新账户信息
        account_array = GetBaseData.getAccounts()
        account_array[ADD_DATA_ACCOUNT_INDEX] = (current_year, current_index)
        
        # 7. 写入数据
        WriteBaseData.writeAccounts(account_array)
        WriteBaseData.appendRawData(raw_data)
        WriteBaseData.writeJsonData(DATA_STATUS_FILE, cur_data_status)
        
        return 0, f"数据添加成功，期号:{epochIndex}, 数字为百位:{hundreds}, 十位:{tens}, 个位:{ones}"
        
    except Exception as e:
        err = traceback.format_exc()
        return 3, f"系统错误: {str(e)}"
    
def predict():
    try:
        # 获取当前年份和当前期数
        account_array = GetBaseData.getAccounts()
        base_prob = GetBaseData.getBaseProb()
        cur_data_status = GetBaseData.getDataStatus()
        raw_data = GetBaseData.getRawData()
        current_year, current_index = account_array[ADD_DATA_ACCOUNT_INDEX]
        next_current_year, next_current_index = BaseCommonFunc.addIndex(current_year, current_index)
        final_res, all_res, merge_res, filter_res, enhance_res, _, _, _ = Predictor.predict(base_prob, cur_data_status)
        return f"{next_current_year}{next_current_index}", final_res, all_res, {}
    except Exception as e:
        err = traceback.format_exc()
        print(f"错误: 参数错误 {err}")
        return "", {}, {}, {} 

    
if __name__ == "__main__":
    try:
        addData()
    except Exception as e:
        print(f"发生错误: {e}")
        exit(1)
    print("数据添加成功")

