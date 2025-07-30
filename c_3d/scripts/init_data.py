from .common import ACCOUNT_FILE, DATA_STATUS_FILE
from .common import PAIR_PROB, TUPLE_PROB, ODD_EVEN_RATIO, SUM_PROB, DIFF_PROB, NUMBER, INIT_DATA_STATUS_ACCOUNT_INDEX, INIT_SUM_BREAK_THRESHOLD, INIT_DIFF_BREAK_THRESHOLD, DATA_INDEX_NAME, INIT_NUMBER_OF_DATA
from .common import BaseCommonFunc
from .common import GetBaseData, WriteBaseData
from .data_status import DataOperator
import json
import traceback
from collections import defaultdict
def initDataStatus():
    try:
        # 初始化基础概率
        base_map = GetBaseData.getBaseProb()
        data_status = {}
        for key in base_map.keys():
            if isinstance(base_map[key], dict):
                data_status[key] = {k: 0 for k, v in base_map[key].items()}
            else:
                data_status[key] = 0
        return data_status
    except Exception as e:
        raise Exception(f"初始化数据失败: {e}")
    

def canBreak(deal_map): 
    if not NUMBER in deal_map or not SUM_PROB in deal_map or not DIFF_PROB in deal_map:
        return False
    canNumSplit = True
    for num in range(0, 10):
        if str(num) not in deal_map[NUMBER]:
            canNumSplit = False
            break
    sum_prob = 0.0
    for key, value in deal_map[SUM_PROB].items():
        sum_prob += value
    diff_prob = 0.0
    for key, value in deal_map[DIFF_PROB].items():
        diff_prob += value
    return canNumSplit and sum_prob >= INIT_SUM_BREAK_THRESHOLD and diff_prob >= INIT_DIFF_BREAK_THRESHOLD

def normalDataStatus(data_status):
    try:
        # 获取原始数据
        raw_data = GetBaseData.getRawData()
        base_prob = GetBaseData.getBaseProb()

        raw_data_len = len(raw_data)
        break_flag = False
        raw_data_index = 0

        prob_map = {}

        while (not break_flag  or raw_data_index < INIT_NUMBER_OF_DATA) and raw_data_index < raw_data_len:
            record = raw_data[raw_data_index]
            raw_data_index += 1
            if not record:
                continue
            
            # 处理每条记录
            new_prob_map = DataOperator.updateRtDataStatus(record, data_status, base_prob)

            for key, value in new_prob_map.items():
                try:
                    if isinstance(value, dict):
                        if key not in prob_map:
                            prob_map[key] = defaultdict(dict)
                        prob_map[key].update(new_prob_map[key])
                    else:
                        if key not in prob_map:
                            prob_map[key] = defaultdict(float)
                        prob_map[key]= new_prob_map[key]
                except Exception as e:
                    err_msg = traceback.format_exc()
                    raise Exception(f"{key} 更新数据失败: {err_msg}")

            if canBreak(prob_map):
                break_flag = True
            
        
        print("数据标准化已完成", raw_data_index)
        return raw_data[raw_data_index][DATA_INDEX_NAME], data_status
    
    except Exception as e:
        err_msg = traceback.format_exc()
        raise Exception(f"处理数据状态失败: {err_msg}")
    

if __name__ == "__main__":
    try:
        # 初始化数据状态
        data_status = initDataStatus()
        
        # 处理数据状态
        raw_data_index, data_status = normalDataStatus(data_status)

        account_array = GetBaseData.getAccounts()

        # 保存数据状态
        current_year, current_index = BaseCommonFunc.splitDataIndex(raw_data_index)
        if len(account_array) <= INIT_DATA_STATUS_ACCOUNT_INDEX:
            account_array.append((current_year, current_index))
        else:
            account_array[INIT_DATA_STATUS_ACCOUNT_INDEX] = (current_year, current_index)
        
        WriteBaseData.writeAccounts(account_array)
        WriteBaseData.writeJsonData(DATA_STATUS_FILE, data_status)
        
        print("数据状态初始化成功")
    except Exception as e:
        err_msg = traceback.format_exc()
        print(f"发生错误: {err_msg}")
        exit(1)